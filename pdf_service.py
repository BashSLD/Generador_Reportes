"""
Servicio de generación de PDFs usando WeasyPrint
"""
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import List
import io
from pathlib import Path

from models import SiteVisitData
from image_processor import ImageProcessor
from config import settings
from datetime import datetime

class PDFGenerator:
    """Generador de PDFs desde templates HTML"""
    
    def __init__(self):
        """Inicializa el generador con el entorno de templates Jinja2"""
        template_dir = Path(__file__).resolve().parent / "templates"
        self.base_dir = template_dir.parent
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.image_processor = ImageProcessor()
    
    def generate_site_visit_pdf(
        self,
        data: SiteVisitData,
        images_bytes: List[bytes]
    ) -> tuple[bytes, dict]:
        """
        Genera PDF de reporte de visita a obra
        
        Args:
            data: Datos del formulario validados
            images_bytes: Lista de bytes de imágenes
        
        Returns:
            Tuple de (pdf_bytes, metadata)
        """
        processed_images, images_metadata = self.image_processor.process_images_for_pdf(
            images_bytes
        )
        
        total_original = sum(m['original_size_bytes'] for m in images_metadata)
        total_optimized = sum(m['optimized_size_bytes'] for m in images_metadata)
        
        template = self.env.get_template('site_visit.html')
        
        html_content = template.render(
            data=data,
            images=processed_images,
            total_images=len(processed_images)
        )

        pdf_io = io.BytesIO()
        HTML(string=html_content, base_url=str(self.base_dir)).write_pdf(
            target=pdf_io,
            optimize_images=True
        )
        pdf_bytes = pdf_io.getvalue()
        
        metadata = {
            'pdf_size_bytes': len(pdf_bytes),
            'images_count': len(images_bytes),
            'total_original_images_size': total_original,
            'total_optimized_images_size': total_optimized,
            'total_compression_ratio': round(total_original / total_optimized, 2) if total_optimized > 0 else 0,
            'images_metadata': images_metadata
        }
        
        return pdf_bytes, metadata
    
    def generate_filename(self, data: SiteVisitData) -> str:
        """
        Genera nombre de archivo descriptivo para el PDF
        
        Args:
            data: Datos del reporte
        
        Returns:
            Nombre de archivo sin extensión
        """
        # Limpiar caracteres especiales del nombre
        nombre_limpio = "".join(
            c if c.isalnum() or c in ('-', '_') else '_' 
            for c in data.nombre_planta
        )[:50]
        
        fecha_valor = data.fecha if data.fecha else datetime.now().strftime("%d-%m-%Y")
        fecha_limpia = fecha_valor.replace('/', '-')
        filename = f"visita_obra_{data.numero_visita}_{nombre_limpio}_{fecha_limpia}"
        
        return filename
