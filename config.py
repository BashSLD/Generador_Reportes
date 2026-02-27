"""
Configuración de la aplicación usando Pydantic Settings
"""
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    APP_NAME: str = "PDF Generator Service"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    MAX_IMAGE_WIDTH: int = Field(default=800, gt=0)  # Ancho máximo en píxeles
    IMAGE_QUALITY: int = Field(default=85, ge=1, le=100)  # Calidad JPEG (1-100)
    MAX_IMAGE_SIZE_MB: int = Field(default=10, gt=0)  # Tamaño máximo por imagen
    
    PDF_DPI: int = 96  # DPI para renderizado
    
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
