"""
Configuración de la aplicación
Lee variables de entorno desde .env
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Configuración general de la aplicación"""
    
    # Base de Datos (solo string URL)
    DATABASE_URL: str
    
    # Rutas del Modelo IA
    MODEL_BASE_PATH: str
    LORA_PATH: str
    
    # Servidor
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # Configuración IA
    MAX_TOKENS: int = 200
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    
    # Logs
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/api.log"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Debug
    DEBUG: bool = True
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convierte string de orígenes a lista"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()

# Crear directorio de logs si no existe
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)