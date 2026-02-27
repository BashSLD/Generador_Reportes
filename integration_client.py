import httpx
import json
from typing import List, Optional
from pathlib import Path


class PDFGeneratorClient:
    """Cliente para comunicarse con el servicio de generación de PDFs"""
    
    def __init__(self, base_url: str = "http://pdf-service:8000"):
        """
        Inicializa el cliente
        
        Args:
            base_url: URL base del servicio PDF
                     - Local: http://localhost:8000
                     - Railway interno: http://pdf-service:8000
                     - Railway externo: https://tu-servicio.up.railway.app
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = 60.0
    
    async def generate_site_visit_report(
        self,
        data: dict,
        image_paths: Optional[List[Path]] = None,
        image_bytes: Optional[List[bytes]] = None
    ) -> bytes:
        """
        Genera PDF de reporte de visita a obra
        
        Args:
            data: Diccionario con datos del formulario
            image_paths: Lista de rutas a archivos de imagen (opcional)
            image_bytes: Lista de bytes de imágenes (opcional)
        
        Returns:
            bytes del PDF generado
        
        Raises:
            httpx.HTTPError: Si hay error en la comunicación
            ValueError: Si los datos son inválidos
        
        Example:
            ```python
            client = PDFGeneratorClient("http://localhost:8000")
            
            data = {
                "nombre_planta": "Planta Solar",
                "id_proyecto": "ABC123",
                "numero_visita": 1,
                # ... resto de campos
            }
            
            image_paths = [
                Path("foto1.jpg"),
                Path("foto2.jpg")
            ]
            
            pdf_bytes = await client.generate_site_visit_report(
                data=data,
                image_paths=image_paths
            )
            
            # Guardar o enviar por email
            with open("reporte.pdf", "wb") as f:
                f.write(pdf_bytes)
            ```
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            files = []
            
            if image_paths:
                for path in image_paths:
                    with open(path, 'rb') as f:
                        files.append(
                            ('images', (path.name, f.read(), 'image/jpeg'))
                        )
            
            elif image_bytes:
                for idx, img_bytes in enumerate(image_bytes):
                    files.append(
                        ('images', (f'image_{idx}.jpg', img_bytes, 'image/jpeg'))
                    )
            
            else:
                raise ValueError("Debe proporcionar image_paths o image_bytes")
            
            
            response = await client.post(
                f"{self.base_url}/api/reports/site-visit",
                data={'data': json.dumps(data)},
                files=files
            )
            
            response.raise_for_status()
            
            return response.content
    
    async def preview_site_visit_report(
        self,
        data: dict,
        image_count: int
    ) -> dict:
        """
        Obtiene metadata sin generar el PDF (útil para validación)
        
        Args:
            data: Diccionario con datos del formulario
            image_count: Cantidad de imágenes
        
        Returns:
            Diccionario con metadata estimada
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            dummy_images = [
                ('images', (f'img_{i}.jpg', b'dummy', 'image/jpeg'))
                for i in range(image_count)
            ]
            
            response = await client.post(
                f"{self.base_url}/api/reports/site-visit/preview",
                data={'data': json.dumps(data)},
                files=dummy_images
            )
            
            response.raise_for_status()
            
            return response.json()
    
    async def health_check(self) -> bool:
        """
        Verifica que el servicio esté disponible
        
        Returns:
            True si el servicio está operacional
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except httpx.HTTPError:
            return False
