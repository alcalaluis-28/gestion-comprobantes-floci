"""Simulación de extracción de datos de comprobantes (Textract mock).

La consigna académica solicita simular Textract y devolver un JSON estructurado
tanto para boletas como facturas, con desglose de emisor, importes e IGV,
identificando claramente los datos como simulados.
"""
from datetime import datetime, timezone
import hashlib


def generar_correlativo(seed_texto: str, prefijo: str = "001") -> str:
    """Genera un correlativo numérico pseudo-determinista a partir del nombre o timestamp."""
    hash_val = int(hashlib.md5(seed_texto.encode("utf-8")).hexdigest()[:6], 16)
    return f"{prefijo}-{hash_val % 900000 + 100000}"


def analizar_comprobante(
    nombre_archivo: str,
    tipo_comprobante: str = "boleta",
    tienda: str = "Chincha",
    fecha: str = None,
    usuario: str = None,
    observacion: str = None,
) -> dict:
    """Genera una estructura JSON simulada de Amazon Textract para boletas o facturas.

    Args:
        nombre_archivo: Nombre del archivo de imagen analizado.
        tipo_comprobante: 'boleta' o 'factura'.
        tienda: Sede de la tienda ('Chincha', 'Pisco', 'Ica').
        fecha: Fecha de emisión en formato YYYY-MM-DD (opcional).
        usuario: Nombre del operador o cliente (opcional).
        observacion: Notas adicionales opcionales.

    Returns:
        dict: Estructura JSON completa que simula la respuesta de extracción OCR de Textract.
    """
    ahora_utc = datetime.now(timezone.utc).isoformat()
    fecha_emision = fecha or datetime.now().strftime("%Y-%m-%d")
    es_factura = str(tipo_comprobante).strip().lower() == "factura"

    # Datos del emisor contextualizados a la región Ica (Chincha, Pisco, Ica)
    sedes_direcciones = {
        "Chincha": "Av. Mariscal Benavides 450, Chincha Alta, Ica",
        "Pisco": "Calle San Martín 210, Pisco, Ica",
        "Ica": "Av. San Martín 880, Cercado de Ica, Ica",
    }
    tienda_normalizada = tienda.title() if tienda else "Chincha"
    direccion_emisor = sedes_direcciones.get(tienda_normalizada, f"Sede {tienda_normalizada}, Ica, Perú")

    # Correlativo simulado
    serie = "F001" if es_factura else "B001"
    correlativo = generar_correlativo(f"{nombre_archivo}-{fecha_emision}", serie)

    # Catálogo de ítems simulados según tipo de comprobante
    if es_factura:
        items = [
            {
                "codigo": "PRD-101",
                "descripcion": f"Material de oficina y suministros sede {tienda_normalizada}",
                "unidad": "NIU",
                "cantidad": 2,
                "precio_unitario": 125.00,
                "valor_venta": 250.00,
                "confianza": 99.2,
            },
            {
                "codigo": "SRV-204",
                "descripcion": "Servicio de mantenimiento y soporte técnico local",
                "unidad": "ZZ",
                "cantidad": 1,
                "precio_unitario": 150.00,
                "valor_venta": 150.00,
                "confianza": 98.7,
            },
        ]
        subtotal = 400.00
        igv = round(subtotal * 0.18, 2)  # 72.00 (18% en Perú)
        total = round(subtotal + igv, 2)  # 472.00
        monto_en_letras = "CUATROCIENTOS SETENTA Y DOS CON 00/100 SOLES"

        cliente_info = {
            "tipo_documento": "RUC",
            "numero_documento": "20547896321",
            "razon_social": f"CORPORACIÓN LOGÍSTICA {tienda_normalizada.upper()} S.A.C.",
            "direccion": f"Zona Industrial S/N, {tienda_normalizada}, Ica",
            "confianza": 97.9,
        }
    else:
        # Boleta de venta
        items = [
            {
                "codigo": "CON-015",
                "descripcion": f"Artículos de librería y consumibles {tienda_normalizada}",
                "unidad": "NIU",
                "cantidad": 3,
                "precio_unitario": 20.00,
                "valor_venta": 60.00,
                "confianza": 98.9,
            },
            {
                "codigo": "CON-088",
                "descripcion": "Papel bond A4 75g millar",
                "unidad": "PK",
                "cantidad": 2,
                "precio_unitario": 17.50,
                "valor_venta": 35.00,
                "confianza": 99.1,
            },
        ]
        subtotal = round(95.00 / 1.18, 2)  # 80.51
        total = 95.00
        igv = round(total - subtotal, 2)  # 14.49
        monto_en_letras = "NOVENTA Y CINCO CON 00/100 SOLES"

        cliente_info = {
            "tipo_documento": "DNI",
            "numero_documento": "47852369",
            "nombre_completo": usuario or "CLIENTE REGISTRADO",
            "confianza": 96.8,
        }

    return {
        "metadatos_extraccion": {
            "servicio": "Amazon Textract (Simulación Floci)",
            "es_simulado": True,
            "version_motor": "v1.2-simulated",
            "fecha_procesamiento": ahora_utc,
            "archivo_analizado": nombre_archivo,
            "confianza_general": 98.5,
            "nota_academica": "Extracción generada por simulación local para entorno Floci. No realiza llamada a API de AWS real.",
        },
        "comprobante": {
            "tipo": "FACTURA ELECTRÓNICA" if es_factura else "BOLETA DE VENTA ELECTRÓNICA",
            "serie": serie,
            "numero_completo": correlativo,
            "fecha_emision": fecha_emision,
            "moneda": "PEN",
            "simbolo_moneda": "S/",
            "forma_pago": "Contado",
            "observacion_registrada": observacion or "Sin observaciones",
        },
        "emisor": {
            "ruc": "20601845923",
            "razon_social": "DISTRIBUIDORA Y COMERCIAL DEL SUR S.A.C.",
            "nombre_comercial": "COMERCIAL SUR ICA",
            "tienda_sede": tienda_normalizada,
            "direccion_fiscal": direccion_emisor,
            "telefono": "(056) 215480",
            "confianza": 99.4,
        },
        "cliente": cliente_info,
        "items": items,
        "importes": {
            "subtotal": subtotal,
            "tasa_igv_porcentaje": 18.0,
            "igv": igv,
            "total": total,
            "monto_en_letras": monto_en_letras,
            "confianza": 99.0,
        },
        "lineas_texto_detectadas": [
            "DISTRIBUIDORA Y COMERCIAL DEL SUR S.A.C.",
            f"RUC: 20601845923 - Sede {tienda_normalizada}",
            f"{'FACTURA ELECTRÓNICA' if es_factura else 'BOLETA DE VENTA ELECTRÓNICA'}: {correlativo}",
            f"FECHA: {fecha_emision}",
            f"TOTAL: S/ {total:.2f}",
        ],
    }
