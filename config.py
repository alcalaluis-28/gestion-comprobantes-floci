"""Configuración de la aplicación y conexión local con Floci."""
import os
from dotenv import load_dotenv

# Asegurar carga del archivo .env desde el directorio raíz del proyecto con precedencia
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, ".env")
load_dotenv(env_path, override=True)


def _normalizar_endpoint(url: str) -> str:
    """Normaliza el endpoint local para garantizar conexión con Floci sin fallos DNS."""
    if not url:
        return "http://localhost:4566"
    url_limpia = url.strip()
    if "localhost.floci.io" in url_limpia:
        url_limpia = url_limpia.replace("localhost.floci.io", "localhost")
    return url_limpia


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-en-desarrollo")
    AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    AWS_ENDPOINT_URL = _normalizar_endpoint(os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"))
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "comprobantes-floci")
    DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "comprobantes")
