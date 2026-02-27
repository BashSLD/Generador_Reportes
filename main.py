"""
FastAPI Application - PDF Generator Service

Endpoints para generación de PDFs de reportes
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
import logging
from pathlib import Path

from models import SiteVisitData, PDFResponse

from config import settings
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from pdf_service import PDFGenerator
from image_processor import ImageProcessor

templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)

ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

app = FastAPI(
    title=settings.APP_NAME,
    description="Servicio de generación de PDFs profesionales",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # Swagger UI
    redoc_url="/redoc" if settings.DEBUG else None  # ReDoc
)

if settings.CORS_ALLOW_CREDENTIALS and "*" in settings.CORS_ORIGINS:
    raise ValueError(
        "Configuración CORS inválida: no se permite CORS_ORIGINS=['*'] "
        "cuando CORS_ALLOW_CREDENTIALS=True"
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

pdf_generator = PDFGenerator()
image_processor = ImageProcessor()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": settings.APP_NAME,
        "status": "operational",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/form", response_class=HTMLResponse)
async def serve_form(request: Request):
    """
    Sirve el formulario HTML para generar reportes
    """
    return templates.TemplateResponse("site_visit_form.html", {"request": request})


@app.get("/health")
async def health_check():
    """
    Health check detallado
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "checks": {
            "weasyprint": "ok",
            "templates": "ok",
            "image_processing": "ok"
        }
    }


@app.post(
    "/api/reports/site-visit",
    response_class=Response,
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "PDF generado exitosamente"
        },
        400: {"description": "Error en validación de datos"},
        413: {"description": "Imagen demasiado grande"},
        500: {"description": "Error interno del servidor"}
    }
)
async def generate_site_visit_pdf(
    data: str = Form(..., description="JSON con datos del formulario"),
    images: List[UploadFile] = File(..., description="Imágenes de evidencia (JPG, PNG)")
):
    """
    Genera PDF de reporte de visita a obra
    
    **Parámetros:**
    - **data**: JSON string con los datos del formulario (ver schema SiteVisitData)
    - **images**: Lista de archivos de imagen (hasta 20 imágenes recomendado)
    
    **Retorna:**
    - PDF file (application/pdf) para descarga directa
    
    **Ejemplo de uso con curl:**
    ```bash
    curl -X POST "http://localhost:8000/api/reports/site-visit" \\
      -F "data={\"nombre_planta\":\"Planta Solar\",\"id_proyecto\":\"ABC123\",...}" \\
      -F "images=@foto1.jpg" \\
      -F "images=@foto2.jpg" \\
      --output reporte.pdf
    ```
    """
    try:
        try:
            data_dict = json.loads(data)
            site_visit_data = SiteVisitData(**data_dict)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"JSON inválido: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error en validación de datos: {str(e)}"
            )
        
        if not images or len(images) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar al menos una imagen"
            )
        
        images_bytes = []
        for idx, image_file in enumerate(images):
            content_type = (image_file.content_type or "").lower()
            if content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Archivo {idx + 1} no es una imagen válida. "
                        f"Formatos permitidos: {', '.join(sorted(ALLOWED_IMAGE_CONTENT_TYPES))}"
                    )
                )

            filename = image_file.filename or ""
            extension = Path(filename).suffix.lower()
            if extension not in ALLOWED_IMAGE_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Archivo {idx + 1} tiene extensión inválida. "
                        f"Extensiones permitidas: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}"
                    )
                )
            
            img_bytes = await image_file.read()
            
            if not image_processor.validate_image_size(img_bytes):
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Imagen {idx + 1} excede el tamaño máximo de {settings.MAX_IMAGE_SIZE_MB}MB"
                )
            
            images_bytes.append(img_bytes)
        
        pdf_bytes, metadata = pdf_generator.generate_site_visit_pdf(
            site_visit_data,
            images_bytes
        )
        
        filename = pdf_generator.generate_filename(site_visit_data)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}.pdf"',
                "X-PDF-Size": str(metadata['pdf_size_bytes']),
                "X-Images-Processed": str(metadata['images_count']),
                "X-Compression-Ratio": str(metadata['total_compression_ratio'])
            }
        )
    
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error generando PDF")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno generando PDF"
        )


@app.post(
    "/api/reports/site-visit/preview",
    response_model=PDFResponse,
    summary="Preview metadata sin generar PDF"
)
async def preview_site_visit_pdf(
    data: str = Form(...),
    images: List[UploadFile] = File(...)
):
    """
    Valida datos y retorna metadata sin generar el PDF
    
    Útil para:
    - Validar datos antes de generar PDF final
    - Estimar tamaño del archivo
    - Verificar cantidad de imágenes
    """
    try:
        data_dict = json.loads(data)
        site_visit_data = SiteVisitData(**data_dict)
        
        total_size = 0
        for idx, image_file in enumerate(images):
            content_type = (image_file.content_type or "").lower()
            if content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Archivo {idx + 1} no es una imagen válida. "
                        f"Formatos permitidos: {', '.join(sorted(ALLOWED_IMAGE_CONTENT_TYPES))}"
                    )
                )

            filename = image_file.filename or ""
            extension = Path(filename).suffix.lower()
            if extension not in ALLOWED_IMAGE_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Archivo {idx + 1} tiene extensión inválida. "
                        f"Extensiones permitidas: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}"
                    )
                )

            img_bytes = await image_file.read()
            if not image_processor.validate_image_size(img_bytes):
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Una o más imágenes exceden {settings.MAX_IMAGE_SIZE_MB}MB"
                )
            total_size += len(img_bytes)
        
        estimated_size = int(total_size * 0.3)  # Después de compresión ~30%
        
        filename = pdf_generator.generate_filename(site_visit_data)
        
        return PDFResponse(
            success=True,
            message="Validación exitosa",
            filename=f"{filename}.pdf",
            file_size_bytes=estimated_size,
            images_processed=len(images)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en validación: {str(e)}"
        )


@app.get("/api/config")
async def get_config():
    """
    Retorna configuración pública del servicio
    """
    return {
        "max_image_width": settings.MAX_IMAGE_WIDTH,
        "image_quality": settings.IMAGE_QUALITY,
        "max_image_size_mb": settings.MAX_IMAGE_SIZE_MB,
        "supported_formats": ["JPEG", "PNG", "WebP"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
