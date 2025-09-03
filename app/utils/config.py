import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Carga las variables de entorno desde un archivo .env
load_dotenv()

class Settings(BaseSettings):
    # Configuración de la base de datos
    DB_URL: str

    # Configuración del almacenamiento (Storage)
    STORAGE_TYPE: str = "local"
    STORAGE_BUCKET: str = "uploads"
    STORAGE_LOCAL_PATH: str = "./storage"
    GCS_CREDENTIALS_PATH: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str | None = None

    # Configuración de la aplicación
    SECRET_KEY: str = "your-secret-key-change-in-production"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8501

    # Configuración opcional de Redis para caché
    REDIS_URL: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Instancia única de la configuración para ser usada en toda la aplicación
settings = Settings()
