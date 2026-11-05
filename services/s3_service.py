"""Operaciones Amazon S3 mediante Boto3 y endpoint local Floci."""
import os
import uuid
import mimetypes
import boto3
from botocore.exceptions import ClientError
from config import Config


EXTENSIONES_PERMITIDAS = {".jpg", ".jpeg", ".png"}
MIMETYPES_PERMITIDOS = {"image/jpeg", "image/png"}


def cliente_s3():
    """Retorna cliente Boto3 S3 configurado para Floci."""
    return boto3.client(
        "s3",
        endpoint_url=Config.AWS_ENDPOINT_URL,
        region_name=Config.AWS_REGION,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    )


def asegurar_bucket(nombre_bucket: str = None) -> bool:
    """Verifica si el bucket existe en S3/Floci; si no existe, lo crea automáticamente."""
    bucket = nombre_bucket or Config.AWS_S3_BUCKET
    s3 = cliente_s3()

    try:
        s3.head_bucket(Bucket=bucket)
        return True
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        # 404 / NoSuchBucket -> crear el bucket
        if error_code in ("404", "NoSuchBucket"):
            try:
                if Config.AWS_REGION == "us-east-1":
                    s3.create_bucket(Bucket=bucket)
                else:
                    s3.create_bucket(
                        Bucket=bucket,
                        CreateBucketConfiguration={"LocationConstraint": Config.AWS_REGION},
                    )
                return True
            except ClientError as ce:
                raise RuntimeError(f"Error al crear el bucket {bucket}: {ce}") from ce
        else:
            # Si ocurrió otro error (e.g. permisos) intentar crearlo
            try:
                s3.create_bucket(Bucket=bucket)
                return True
            except Exception as ex:
                raise RuntimeError(f"No se pudo verificar ni crear el bucket {bucket}: {ex}") from ex


def subir_imagen(
    archivo_bytes_o_stream,
    nombre_original: str,
    content_type: str = None,
    nombre_bucket: str = None,
) -> dict:
    """Sube una imagen JPG o PNG al bucket S3 con un identificador único.

    Args:
        archivo_bytes_o_stream: bytes o stream (con .read()) del archivo.
        nombre_original: nombre de archivo proporcionado (e.g. factura1.png).
        content_type: MIME type explícito opcional.
        nombre_bucket: nombre opcional del bucket S3.

    Returns:
        dict: metadatos del objeto subido (s3_key, bucket, nombre_original, content_type, tamano_bytes).
    """
    bucket = nombre_bucket or Config.AWS_S3_BUCKET
    asegurar_bucket(bucket)

    # Validar extensión
    _, ext = os.path.splitext(nombre_original.lower())
    if ext not in EXTENSIONES_PERMITIDAS:
        raise ValueError(f"Extensión no permitida: {ext}. Solo se admiten: {', '.join(sorted(EXTENSIONES_PERMITIDAS))}")

    # Determinar Content-Type
    tipo_mime = content_type or mimetypes.guess_type(nombre_original)[0]
    if not tipo_mime or tipo_mime not in MIMETYPES_PERMITIDOS:
        tipo_mime = "image/png" if ext == ".png" else "image/jpeg"

    # Leer contenido a bytes si es un stream
    if hasattr(archivo_bytes_o_stream, "read"):
        contenido_bytes = archivo_bytes_o_stream.read()
    elif isinstance(archivo_bytes_o_stream, (bytes, bytearray)):
        contenido_bytes = bytes(archivo_bytes_o_stream)
    else:
        raise TypeError("archivo_bytes_o_stream debe ser bytes o un objeto con método .read()")

    # Generar clave única con UUID
    nombre_limpio = os.path.basename(nombre_original).replace(" ", "_")
    s3_key = f"comprobantes/{uuid.uuid4().hex}_{nombre_limpio}"

    s3 = cliente_s3()
    s3.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=contenido_bytes,
        ContentType=tipo_mime,
        Metadata={
            "nombre_original": nombre_limpio,
            "subido_por": "sistema_comprobantes",
        },
    )

    return {
        "s3_key": s3_key,
        "bucket": bucket,
        "nombre_original": nombre_limpio,
        "content_type": tipo_mime,
        "tamano_bytes": len(contenido_bytes),
    }


def obtener_imagen(s3_key: str, nombre_bucket: str = None) -> dict:
    """Obtiene una imagen de S3 a partir de su clave única.

    Returns:
        dict con 'body' (bytes), 'content_type' y 'content_length'.
    """
    bucket = nombre_bucket or Config.AWS_S3_BUCKET
    s3 = cliente_s3()

    try:
        response = s3.get_object(Bucket=bucket, Key=s3_key)
        return {
            "body": response["Body"].read(),
            "content_type": response.get("ContentType", "application/octet-stream"),
            "content_length": response.get("ContentLength", 0),
        }
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "NoSuchKey":
            raise FileNotFoundError(f"Imagen no encontrada en S3: {s3_key}") from e
        raise


def eliminar_imagen(s3_key: str, nombre_bucket: str = None) -> bool:
    """Elimina una imagen de S3."""
    bucket = nombre_bucket or Config.AWS_S3_BUCKET
    s3 = cliente_s3()

    try:
        s3.delete_object(Bucket=bucket, Key=s3_key)
        return True
    except ClientError as e:
        raise RuntimeError(f"Error al eliminar la imagen {s3_key} de S3: {e}") from e
