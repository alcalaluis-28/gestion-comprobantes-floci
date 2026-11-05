"""Aplicación web para la Gestión de Comprobantes con AWS Floci.

Servicios integrados:
- Amazon S3 (local en Floci): Almacenamiento de imágenes JPG/PNG.
- Amazon DynamoDB (local en Floci): Persistencia de metadatos y registros.
- Amazon Textract (simulación): Extracción estructurada de datos en formato JSON.
"""
import os
import re
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify, Response
from werkzeug.utils import secure_filename

from config import Config
from services import (
    asegurar_bucket,
    subir_imagen,
    obtener_imagen,
    eliminar_imagen,
    asegurar_tabla,
    guardar_comprobante,
    listar_comprobantes,
    obtener_comprobante,
    eliminar_comprobante,
    analizar_comprobante,
)

app = Flask(__name__)
app.config.from_object(Config)

# Extensiones y tipos MIME permitidos
EXTENSIONES_PERMITIDAS = {".jpg", ".jpeg", ".png"}
MIMETYPES_PERMITIDOS = {"image/jpeg", "image/png"}
TIENDAS_VALIDAS = {"Chincha", "Pisco", "Ica"}
TIPOS_VALIDOS = {"boleta", "factura"}


def inicializar_infraestructura():
    """Garantiza que el bucket S3 y la tabla DynamoDB existan al iniciar la app."""
    try:
        asegurar_bucket()
        asegurar_tabla()
        app.logger.info("Infraestructura S3 y DynamoDB verificada en Floci.")
    except Exception as e:
        app.logger.warning(f"Aviso de inicialización AWS/Floci: {e}")


# Intentar inicializar recursos al cargar el módulo
inicializar_infraestructura()


# -------------------------------------------------------------------------
# Rutas Principales
# -------------------------------------------------------------------------

@app.get("/")
def index():
    """Renderiza la vista principal del panel de gestión."""
    return render_template("index.html")


@app.get("/health")
def health():
    """Comprobación de estado general y endpoints de Floci."""
    return jsonify({
        "status": "ok",
        "application": "comprobantes-floci",
        "floci_endpoint": Config.AWS_ENDPOINT_URL,
        "s3_bucket": Config.AWS_S3_BUCKET,
        "dynamodb_table": Config.DYNAMODB_TABLE,
        "region": Config.AWS_REGION,
    })


# -------------------------------------------------------------------------
# API REST de Comprobantes
# -------------------------------------------------------------------------

@app.get("/api/comprobantes")
def api_listar_comprobantes():
    """Retorna todos los comprobantes y calcula el resumen dinámico basado en datos reales."""
    try:
        registros = listar_comprobantes()

        # Cálculo dinámico de indicadores sobre los datos reales
        total_registros = len(registros)
        tiendas_con_registros = {r.get("tienda") for r in registros if r.get("tienda")}
        total_tiendas = len(tiendas_con_registros)
        total_imagenes = sum(1 for r in registros if r.get("s3_key"))

        desglose = {
            "Chincha": sum(1 for r in registros if r.get("tienda") == "Chincha"),
            "Pisco": sum(1 for r in registros if r.get("tienda") == "Pisco"),
            "Ica": sum(1 for r in registros if r.get("tienda") == "Ica"),
        }

        return jsonify({
            "success": True,
            "data": registros,
            "resumen": {
                "total_registros": total_registros,
                "total_tiendas": total_tiendas,
                "total_imagenes": total_imagenes,
                "desglose": desglose,
            },
        })
    except Exception as e:
        app.logger.error(f"Error al listar comprobantes: {e}")
        return jsonify({"success": False, "error": f"Error al consultar DynamoDB: {str(e)}"}), 500


@app.post("/api/comprobantes")
def api_crear_comprobante():
    """Valida los campos, simula Textract, almacena la imagen en S3 y persiste en DynamoDB.

    Si la persistencia en DynamoDB falla, elimina el objeto subido a S3 (rollback de imagen huérfana).
    """
    # 1. Validación de campos de formulario
    tipo = request.form.get("tipo", "").strip().lower()
    fecha = request.form.get("fecha", "").strip()
    usuario = request.form.get("usuario", "").strip()
    tienda = request.form.get("tienda", "").strip().capitalize()
    observacion = request.form.get("observacion", "").strip()

    if tipo not in TIPOS_VALIDOS:
        return jsonify({"success": False, "error": "Tipo de comprobante inválido. Debe ser 'boleta' o 'factura'."}), 400

    if not fecha:
        return jsonify({"success": False, "error": "La fecha de emisión es obligatoria."}), 400

    try:
        datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        return jsonify({"success": False, "error": "Formato de fecha inválido. Utilice AAAA-MM-DD."}), 400

    if not usuario:
        return jsonify({"success": False, "error": "El nombre del usuario/operador es obligatorio."}), 400

    if tienda not in TIENDAS_VALIDAS:
        return jsonify({"success": False, "error": f"Tienda inválida. Opciones permitidas: {', '.join(sorted(TIENDAS_VALIDAS))}."}), 400

    # 2. Validación de archivo de imagen
    if "imagen" not in request.files:
        return jsonify({"success": False, "error": "Debe adjuntar un archivo de imagen (JPG o PNG)."}), 400

    archivo = request.files["imagen"]
    if not archivo or not archivo.filename:
        return jsonify({"success": False, "error": "El archivo de imagen no fue seleccionado."}), 400

    nombre_original = secure_filename(archivo.filename) or "comprobante.jpg"
    _, extension = os.path.splitext(nombre_original.lower())
    if extension not in EXTENSIONES_PERMITIDAS:
        return jsonify({
            "success": False,
            "error": f"Formato de archivo no admitido: {extension}. Solo se permiten imágenes JPG, JPEG o PNG.",
        }), 400

    mimetype = archivo.mimetype or ""
    if mimetype and mimetype not in MIMETYPES_PERMITIDOS and mimetype != "application/octet-stream":
        return jsonify({
            "success": False,
            "error": f"Tipo MIME no admitido: {mimetype}. Solo se permiten image/jpeg e image/png.",
        }), 400

    s3_key_subida = None
    try:
        # 3. Simulación de extracción estructurada Textract
        datos_textract = analizar_comprobante(
            nombre_archivo=nombre_original,
            tipo_comprobante=tipo,
            tienda=tienda,
            fecha=fecha,
            usuario=usuario,
            observacion=observacion,
        )

        # 4. Almacenamiento en S3 con clave única
        resultado_s3 = subir_imagen(
            archivo_bytes_o_stream=archivo.stream,
            nombre_original=nombre_original,
            content_type=mimetype if mimetype in MIMETYPES_PERMITIDOS else None,
        )
        s3_key_subida = resultado_s3["s3_key"]

        # 5. Persistencia en DynamoDB
        registro = {
            "tipo": tipo,
            "fecha": fecha,
            "usuario": usuario,
            "tienda": tienda,
            "observacion": observacion,
            "s3_key": s3_key_subida,
            "nombre_archivo": nombre_original,
            "mimetype": resultado_s3["content_type"],
            "tamano_bytes": resultado_s3["tamano_bytes"],
            "datos_textract": datos_textract,
            "numero_comprobante": datos_textract["comprobante"]["numero_completo"],
            "monto_total": datos_textract["importes"]["total"],
            "igv": datos_textract["importes"]["igv"],
            "subtotal": datos_textract["importes"]["subtotal"],
            "fecha_registro": datetime.now(timezone.utc).isoformat(),
        }

        try:
            registro_guardado = guardar_comprobante(registro)
        except Exception as dynamo_error:
            # ROLLBACK: Si falla DynamoDB, eliminar la imagen subida a S3 para evitar archivos huérfanos
            app.logger.error(f"Fallo al guardar en DynamoDB. Iniciando rollback de S3 para {s3_key_subida}: {dynamo_error}")
            try:
                eliminar_imagen(s3_key_subida)
                app.logger.info(f"Rollback exitoso: Imagen {s3_key_subida} eliminada de S3 tras fallo en DynamoDB.")
            except Exception as rollback_err:
                app.logger.critical(f"No se pudo completar el rollback en S3 ({s3_key_subida}): {rollback_err}")
            raise RuntimeError(f"Error al registrar en DynamoDB: {str(dynamo_error)}") from dynamo_error

        return jsonify({
            "success": True,
            "mensaje": "Comprobante procesado, imagen almacenada y registro persistido exitosamente.",
            "comprobante": registro_guardado,
        }), 201

    except Exception as e:
        app.logger.error(f"Error general procesando comprobante: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.get("/api/comprobantes/<id_comprobante>/json")
def api_obtener_json_comprobante(id_comprobante):
    """Retorna los datos simulados de Textract y metadatos asociados al comprobante."""
    try:
        comprobante = obtener_comprobante(id_comprobante)
        if not comprobante:
            return jsonify({"success": False, "error": f"Comprobante con ID '{id_comprobante}' no encontrado."}), 404

        return jsonify({
            "success": True,
            "id": comprobante.get("id"),
            "datos_textract": comprobante.get("datos_textract", {}),
            "metadatos": {
                "tipo": comprobante.get("tipo"),
                "tienda": comprobante.get("tienda"),
                "fecha": comprobante.get("fecha"),
                "usuario": comprobante.get("usuario"),
                "s3_key": comprobante.get("s3_key"),
                "fecha_registro": comprobante.get("fecha_registro"),
            },
        })
    except Exception as e:
        app.logger.error(f"Error al obtener JSON de comprobante {id_comprobante}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.get("/api/comprobantes/<id_comprobante>/imagen")
def api_obtener_imagen_comprobante(id_comprobante):
    """Actúa como proxy seguro de S3 sirviendo el contenido binario de la imagen."""
    try:
        comprobante = obtener_comprobante(id_comprobante)
        if not comprobante:
            return jsonify({"success": False, "error": "Comprobante no encontrado."}), 404

        s3_key = comprobante.get("s3_key")
        if not s3_key:
            return jsonify({"success": False, "error": "El comprobante no tiene una imagen asociada."}), 404

        objeto_s3 = obtener_imagen(s3_key)
        return Response(
            objeto_s3["body"],
            mimetype=objeto_s3["content_type"],
            headers={
                "Cache-Control": "private, max-age=86400",
                "Content-Disposition": f"inline; filename={os.path.basename(s3_key)}",
            },
        )
    except FileNotFoundError:
        return jsonify({"success": False, "error": "La imagen no existe en el almacenamiento S3."}), 404
    except Exception as e:
        app.logger.error(f"Error al servir imagen de {id_comprobante}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.delete("/api/comprobantes/<id_comprobante>")
def api_eliminar_comprobante(id_comprobante):
    """Elimina coordinadamente el registro en DynamoDB y el objeto correspondiente en S3."""
    try:
        comprobante = obtener_comprobante(id_comprobante)
        if not comprobante:
            return jsonify({"success": False, "error": f"Comprobante con ID '{id_comprobante}' no encontrado."}), 404

        s3_key = comprobante.get("s3_key")

        # 1. Eliminar registro de DynamoDB
        eliminar_comprobante(id_comprobante)

        # 2. Eliminar objeto de S3 si existe
        if s3_key:
            try:
                eliminar_imagen(s3_key)
            except Exception as s3_err:
                app.logger.warning(f"Aviso: no se pudo eliminar la imagen {s3_key} en S3: {s3_err}")

        return jsonify({
            "success": True,
            "mensaje": "Comprobante e imagen eliminados coordinadamente de DynamoDB y S3.",
            "id_eliminado": id_comprobante,
        })
    except Exception as e:
        app.logger.error(f"Error al eliminar comprobante {id_comprobante}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
