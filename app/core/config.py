"""
Configurações da aplicação
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # Informações da aplicação
    APP_NAME: str = "Sistema de Gestão de Supermercado"
    APP_VERSION: str = "1.0.0"
    DESCRIPTION: str = "Sistema completo para gestão de supermercado"

    # API
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Segurança
    SECRET_KEY: str = "sua-chave-secreta-super-segura-mude-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Banco de dados
    DATABASE_URL: str = "sqlite:///./supermarket.db"
    DATABASE_URL_DEV: str = "sqlite:///./supermarket_dev.db"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8501",
    ]

    # Hardware
    BARCODE_READER_ENABLED: bool = False
    BARCODE_READER_PORT: str = "auto"
    SCALE_ENABLED: bool = False
    SCALE_PORT: str = "COM1"
    SCALE_BAUDRATE: int = 9600
    PRINTER_ENABLED: bool = False
    PRINTER_PORT: str = "COM2"

    # Logs
    LOG_LEVEL: str = "INFO"

    # Campos extras do .env
    PAYMENT_TERMINAL_ENABLED: bool = False
    ENVIRONMENT: str = "development"
    BACKUP_ENABLED: bool = True
    BACKUP_INTERVAL_HOURS: int = 24

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância singleton das configurações"""
    return Settings()


# Instância global das configurações
settings = get_settings()
