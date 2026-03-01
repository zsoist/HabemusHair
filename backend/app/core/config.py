"""
Configuracion central de la aplicacion.

QUE HACE ESTE ARCHIVO:
Este archivo define todas las variables de configuracion del backend.
En vez de escribir valores "hardcodeados" (fijos) en el codigo,
los ponemos aqui para poder cambiarlos facilmente segun el entorno
(desarrollo local, testing, produccion).

COMO FUNCIONA:
- Usa Pydantic Settings que lee variables de entorno automaticamente.
- Si existe un archivo .env en la raiz del proyecto, lo lee.
- Si una variable no esta en .env, usa el valor por defecto definido aqui.

EJEMPLO:
    Si en tu .env tienes: DATABASE_URL=postgresql://user:pass@localhost/habemus
    Entonces settings.DATABASE_URL tendra ese valor.
    Si no lo tienes, usara el valor por defecto de abajo.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Configuracion de la aplicacion.
    Cada campo aqui es una variable de configuracion.
    """

    # --- Nombre y version ---
    APP_NAME: str = "HabemusHair - Hair Planning Copilot"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True  # En produccion esto debe ser False

    # --- Base de datos ---
    # postgresql://usuario:password@host:puerto/nombre_base_datos
    DATABASE_URL: str = "postgresql://habemus:habemus_dev@localhost:5432/habemus_hair"

    # --- Almacenamiento de imagenes ---
    # MinIO es como un "mini AWS S3" que corre en tu computador
    STORAGE_ENDPOINT: str = "localhost:9000"
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin"
    STORAGE_BUCKET: str = "habemus-images"
    STORAGE_USE_SSL: bool = False

    # --- Seguridad ---
    SECRET_KEY: str = "CAMBIAME-en-produccion-usa-un-valor-aleatorio-largo"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas

    # --- Modelos de ML ---
    # Carpeta donde se guardan los pesos de los modelos entrenados
    MODELS_DIR: str = "models/weights"

    # --- Limites ---
    MAX_IMAGE_SIZE_MB: int = 20  # Tamano maximo de imagen que aceptamos
    MIN_IMAGE_WIDTH: int = 640   # Ancho minimo de imagen en pixeles
    MIN_IMAGE_HEIGHT: int = 480  # Alto minimo de imagen en pixeles

    # --- Redis (para tareas asincronas) ---
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instancia global de configuracion.
# Importa esto en cualquier archivo asi:
#     from app.core.config import settings
#     print(settings.DATABASE_URL)
settings = Settings()
