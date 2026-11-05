"""Configuración de la aplicación y conexión local con Floci."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-en-desarrollo")
    AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost.floci.io:4566")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "comprobantes-floci")
    DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "comprobantes")
