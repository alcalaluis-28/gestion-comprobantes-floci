"""Operaciones Amazon DynamoDB mediante Boto3 y endpoint local Floci."""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError
from config import Config


def recurso_dynamodb():
    """Retorna recurso Boto3 DynamoDB configurado para Floci."""
    return boto3.resource(
        "dynamodb",
        endpoint_url=Config.AWS_ENDPOINT_URL,
        region_name=Config.AWS_REGION,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    )


def cliente_dynamodb():
    """Retorna cliente Boto3 DynamoDB de bajo nivel."""
    return boto3.client(
        "dynamodb",
        endpoint_url=Config.AWS_ENDPOINT_URL,
        region_name=Config.AWS_REGION,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    )


def convertir_a_decimal(obj):
    """Convierte floats y estructuras numéricas a Decimal para compatibilidad con DynamoDB."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: convertir_a_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convertir_a_decimal(item) for item in obj]
    return obj


def convertir_de_decimal(obj):
    """Convierte objetos Decimal de DynamoDB a tipos nativos de Python (int, float) para JSON."""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    if isinstance(obj, dict):
        return {k: convertir_de_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convertir_de_decimal(item) for item in obj]
    return obj


def asegurar_tabla(nombre_tabla: str = None) -> bool:
    """Verifica si la tabla existe en DynamoDB/Floci; si no existe, la crea con PK 'id' (String)."""
    tabla_nombre = nombre_tabla or Config.DYNAMODB_TABLE
    cliente = cliente_dynamodb()

    tablas = cliente.list_tables().get("TableNames", [])
    if tabla_nombre in tablas:
        return True

    # Si no existe, crearla
    recurso = recurso_dynamodb()
    try:
        tabla = recurso.create_table(
            TableName=tabla_nombre,
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        tabla.wait_until_exists()
        return True
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "ResourceInUseException":
            return True
        raise RuntimeError(f"Error al crear tabla DynamoDB {tabla_nombre}: {e}") from e


def guardar_comprobante(registro: dict, nombre_tabla: str = None) -> dict:
    """Guarda un registro de comprobante en DynamoDB.

    Asigna un UUID único si no se provee 'id' y fecha de registro si no existe.
    """
    tabla_nombre = nombre_tabla or Config.DYNAMODB_TABLE
    asegurar_tabla(tabla_nombre)

    item = dict(registro)
    if not item.get("id"):
        item["id"] = uuid.uuid4().hex

    if not item.get("fecha_registro"):
        item["fecha_registro"] = datetime.now(timezone.utc).isoformat()

    item_preparado = convertir_a_decimal(item)
    recurso = recurso_dynamodb()
    tabla = recurso.Table(tabla_nombre)
    tabla.put_item(Item=item_preparado)

    return convertir_de_decimal(item)


def listar_comprobantes(nombre_tabla: str = None) -> list:
    """Lista todos los comprobantes almacenados en DynamoDB."""
    tabla_nombre = nombre_tabla or Config.DYNAMODB_TABLE
    asegurar_tabla(tabla_nombre)

    recurso = recurso_dynamodb()
    tabla = recurso.Table(tabla_nombre)

    items = []
    response = tabla.scan()
    items.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = tabla.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    items_convertidos = [convertir_de_decimal(i) for i in items]
    # Ordenar por fecha_registro descendente
    items_convertidos.sort(
        key=lambda x: (x.get("fecha_registro") or x.get("fecha") or ""),
        reverse=True,
    )
    return items_convertidos


def obtener_comprobante(id_comprobante: str, nombre_tabla: str = None) -> dict | None:
    """Consulta un comprobante por su ID único."""
    tabla_nombre = nombre_tabla or Config.DYNAMODB_TABLE
    asegurar_tabla(tabla_nombre)

    recurso = recurso_dynamodb()
    tabla = recurso.Table(tabla_nombre)

    response = tabla.get_item(Key={"id": id_comprobante})
    item = response.get("Item")
    if not item:
        return None
    return convertir_de_decimal(item)


def eliminar_comprobante(id_comprobante: str, nombre_tabla: str = None) -> bool:
    """Elimina un comprobante por su ID único."""
    tabla_nombre = nombre_tabla or Config.DYNAMODB_TABLE
    asegurar_tabla(tabla_nombre)

    recurso = recurso_dynamodb()
    tabla = recurso.Table(tabla_nombre)

    try:
        tabla.delete_item(Key={"id": id_comprobante})
        return True
    except ClientError as e:
        raise RuntimeError(f"Error al eliminar registro {id_comprobante} de DynamoDB: {e}") from e
