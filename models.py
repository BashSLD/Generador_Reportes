"""
Modelos Pydantic para validación de datos de entrada
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class SiteVisitData(BaseModel):
    """Datos del formulario de visita a obra"""
    
    nombre_planta: str = Field(..., min_length=1, max_length=200)
    id_proyecto: str = Field(..., min_length=1, max_length=50)
    ubicacion: str = Field(default="NA", max_length=200)
    persona_responsable_interna: str = Field(..., max_length=200)
    responsable_obra: str = Field(..., max_length=200)
    
    # Datos de la visita
    numero_visita: int = Field(..., ge=1)
    hora_entrada: str = Field(..., description="Formato: HH:MM")
    hora_salida: str = Field(..., description="Formato: HH:MM")
    motivo_visita: str = Field(..., max_length=2000)
    avances_conforme_cronograma: bool = Field(default=True)
    razon_no_conforme: Optional[str] = Field(default="", max_length=2000)
    acuerdos: Optional[str] = Field(default="", max_length=2000)
    
    # Metadata
    fecha: Optional[str] = Field(default=None)
    lugar_elaboracion: Optional[str] = Field(default="")
    
    @field_validator('fecha', mode='before')
    @classmethod
    def set_fecha_default(cls, v):
        if v is None:
            return datetime.now().strftime("%d/%m/%Y")
        return v
    
    @field_validator('hora_entrada', 'hora_salida')
    @classmethod
    def validate_time_format(cls, v):
        try:
            parts = v.split(':')
            if len(parts) != 2:
                raise ValueError
            hour, minute = int(parts[0]), int(parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
            return f"{hour:02d}:{minute:02d}"
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValueError(f"Formato de hora inválido: {v}. Use HH:MM") from exc
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre_planta": "Planta Solar",
                "id_proyecto": "NMHJJ",
                "ubicacion": "Direccion del proyecto",
                "persona_responsable_interna": "Juan Perez",
                "responsable_obra": "Juan Perez",
                "numero_visita": 33,
                "hora_entrada": "08:09",
                "hora_salida": "10:09",
                "motivo_visita": "Revisión de avance",
                "avances_conforme_cronograma": True,
                "razon_no_conforme": "",
                "acuerdos": "Revisar entrega de materiales próxima semana",
                "fecha": "25/02/2025",
                "lugar_elaboracion": "Querétaro"
            }
        }


class PDFResponse(BaseModel):
    
    success: bool
    message: str
    filename: str
    file_size_bytes: int
    images_processed: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "PDF generado exitosamente",
                "filename": "visita_obra_33_25-02-2025.pdf",
                "file_size_bytes": 2456789,
                "images_processed": 12
            }
        }
