"""Servicios de integración con AWS/Floci."""
from .s3_service import (
    cliente_s3,
    asegurar_bucket,
    subir_imagen,
    obtener_imagen,
    eliminar_imagen,
)
from .dynamodb_service import (
    recurso_dynamodb,
    cliente_dynamodb,
    asegurar_tabla,
    guardar_comprobante,
    listar_comprobantes,
    obtener_comprobante,
    eliminar_comprobante,
)
from .textract_service import analizar_comprobante

__all__ = [
    "cliente_s3",
    "asegurar_bucket",
    "subir_imagen",
    "obtener_imagen",
    "eliminar_imagen",
    "recurso_dynamodb",
    "cliente_dynamodb",
    "asegurar_tabla",
    "guardar_comprobante",
    "listar_comprobantes",
    "obtener_comprobante",
    "eliminar_comprobante",
    "analizar_comprobante",
]
