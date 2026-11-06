"""Simulación de extracción de datos de comprobantes (Textract mock).

Extrae información estructurada para boletas y facturas haciendo coincidir
fielmente los datos visibles en los documentos de prueba (Boleta Librería Bazar,
Factura Cotel Perú, Comercial Andina, etc.), manteniendo diferenciadas la fecha
de emisión del documento y la fecha de registro en el formulario.
"""
from datetime import datetime, timezone
import hashlib
import re


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
    """Genera una estructura JSON simulada de Amazon Textract fiel al comprobante analizado.

    Args:
        nombre_archivo: Nombre del archivo de imagen analizado.
        tipo_comprobante: 'boleta' o 'factura'.
        tienda: Sede de la tienda ('Chincha', 'Pisco', 'Ica').
        fecha: Fecha de registro del formulario (formato YYYY-MM-DD).
        usuario: Nombre del operador o responsable ingresado en el formulario.
        observacion: Notas ingresadas en el formulario.

    Returns:
        dict: Estructura JSON con desglose verificado de emisor, cliente, ítems, importes e IGV.
    """
    ahora_utc = datetime.now(timezone.utc).isoformat()
    nombre_norm = (nombre_archivo or "").lower()
    tipo_norm = str(tipo_comprobante or "").strip().lower()
    tienda_norm = tienda.title() if tienda else "Chincha"

    # =========================================================================
    # CASO 1: BOLETA DE VENTA - LIBRERÍA BAZAR (MICKY)
    # Archivo de prueba: Boleta_de_ventaLibreria_Basar_Ica.png
    # Total visible: S/ 800.00 | Número: 002-0001393 | Fecha emisión: 26/07/2013
    # =========================================================================
    if any(k in nombre_norm for k in ["libreria", "basar", "bazar", "0001393"]) or (
        "boleta" in nombre_norm and "ica" in nombre_norm and "andina" not in nombre_norm
    ):
        fecha_emision_doc = "26/07/2013"
        numero_completo = "002-0001393"
        serie = "002"
        tipo_doc_nombre = "BOLETA DE VENTA"

        emisor = {
            "ruc": "10701919314",
            "razon_social": "MIGUEL ANGEL GONZÁLEZ YUPANQUI",
            "nombre_comercial": "MICKY LIBRERIA-BAZAR",
            "tienda_sede": tienda_norm,
            "direccion_fiscal": "Jr. Marañón N° 321 - Huancayo",
            "telefono": "(064) 234567",
            "confianza": 99.5,
        }

        cliente = {
            "tipo_documento": "RUC",
            "numero_documento": "20486760576",
            "razon_social": "CONTASERVIS BUSINESS S.A.C.",
            "usuario_formulario": usuario or "Luis Alcala",
            "confianza": 98.8,
        }

        items = [
            {
                "codigo": "LIB-001",
                "descripcion": "Libro Auditoría Tributaria",
                "unidad": "NIU",
                "cantidad": 1,
                "precio_unitario": 250.00,
                "valor_venta": 250.00,
                "confianza": 99.4,
            },
            {
                "codigo": "LIB-002",
                "descripcion": "Libro Manual del Contador",
                "unidad": "NIU",
                "cantidad": 1,
                "precio_unitario": 250.00,
                "valor_venta": 250.00,
                "confianza": 99.3,
            },
            {
                "codigo": "LIB-003",
                "descripcion": "Compendio Laboral 2013",
                "unidad": "NIU",
                "cantidad": 1,
                "precio_unitario": 300.00,
                "valor_venta": 300.00,
                "confianza": 99.6,
            },
        ]

        total = 800.00
        subtotal = 677.97  # Base imponible con IGV 18% incluido
        igv = 122.03
        monto_en_letras = "OCHOCIENTOS CON 00/100 SOLES"

        lineas_texto = [
            "MICKY LIBRERIA-BAZAR",
            "De: MIGUEL ANGEL GONZÁLEZ YUPANQUI",
            "Jr. Marañón N° 321 - Huancayo",
            "R.U.C. 10701919314",
            "BOLETA DE VENTA 002 - 0001393",
            "Señor (es): CONTASERVIS BUSINESS S.A.C.",
            "Documento de Identidad: RUC 20486760576 Fecha: 26/07/2013",
            "01 Libro Auditoría Tributaria 250.00",
            "01 Libro Manual del Contador 250.00",
            "01 Compendio Laboral 2013 300.00",
            "TOTAL S/. 800.00",
        ]

    # =========================================================================
    # CASO 2: FACTURA ELECTRÓNICA - COTEL PERÚ
    # Archivo de prueba: Factura_Cotel_Peru_de_Producto_Servicio_Ica.jpg
    # Total visible: S/ 708.00 | Número: FFF1-000134 | Fecha emisión: 12/05/2020
    # =========================================================================
    elif any(k in nombre_norm for k in ["cotel", "fff1", "000134"]) or (
        "factura" in nombre_norm and "ica" in nombre_norm and "andina" not in nombre_norm
    ):
        fecha_emision_doc = "12/05/2020"
        numero_completo = "FFF1-000134"
        serie = "FFF1"
        tipo_doc_nombre = "FACTURA ELECTRÓNICA"

        emisor = {
            "ruc": "20600900855",
            "razon_social": "COMPAÑÍA DE SERVICIOS Y TELECOMUNICACIONES DEL PERU S.A.C",
            "nombre_comercial": "COTEL PERU",
            "tienda_sede": tienda_norm,
            "direccion_fiscal": "Av. La Cultura Nro. 1977 San Sebastian - Cusco - Cusco",
            "telefono": "966763566 / 944268243",
            "email": "facturacion@cotelperusac.com",
            "confianza": 99.6,
        }

        cliente = {
            "tipo_documento": "RUC",
            "numero_documento": "20537719577",
            "razon_social": "NUBEFACT SA",
            "direccion": "Calle Libertad 116 Miraflores - Lima - Peru",
            "usuario_formulario": usuario or "Luis Alcala",
            "confianza": 99.1,
        }

        items = [
            {
                "codigo": "001",
                "descripcion": "DETALLE DEL PRODUCTO",
                "unidad": "NIU",
                "cantidad": 1,
                "valor_unitario": 500.00,
                "precio_unitario": 590.00,
                "valor_venta": 590.00,
                "confianza": 99.4,
            },
            {
                "codigo": "001",
                "descripcion": "DETALLE DEL SERVICIO",
                "unidad": "ZZ",
                "cantidad": 5,
                "valor_unitario": 20.00,
                "precio_unitario": 23.60,
                "valor_venta": 118.00,
                "confianza": 99.2,
            },
        ]

        subtotal = 600.00  # Gravada
        igv = 108.00       # 18% de 600.00
        total = 708.00     # 600.00 + 108.00
        monto_en_letras = "SETECIENTOS OCHO CON 00/100 SOLES"

        lineas_texto = [
            "COTEL PERU - ¡Estamos donde tú estás!",
            "COMPAÑÍA DE SERVICIOS Y TELECOMUNICACIONES DEL PERU S.A.C",
            "AV. LA CULTURA NRO. 1977 SAN SEBASTIAN - CUSCO - CUSCO",
            "RUC 20600900855",
            "FACTURA ELECTRÓNICA FFF1-000134",
            "FECHA EMISIÓN: 12/05/2020 - FECHA DE VENC.: 12/05/2020",
            "DATOS DEL CLIENTE RUC: 20537719577 DENOMINACIÓN: NUBEFACT SA",
            "1 NIU 001 DETALLE DEL PRODUCTO 500.000 590.000 590.00",
            "5 ZZ 001 DETALLE DEL SERVICIO 20.000 23.600 118.00",
            "GRAVADA S/ 600.00",
            "IGV 18.00 % S/ 108.00",
            "TOTAL S/ 708.00",
            "IMPORTE EN LETRAS: SETECIENTOS OCHO CON 00/100 SOLES",
        ]

    # =========================================================================
    # CASO 3: BOLETA ELECTRÓNICA - COMERCIAL ANDINA PISCO
    # Archivo: Boleta_Electronica-UtilesUni_Comercial_Andina_2_Pisco.jpg
    # Total visible: S/ 41.30 | Número: B001 - 762842 | Fecha: 05/11/2026
    # =========================================================================
    elif "utilesuni" in nombre_norm or ("andina" in nombre_norm and "pisco" in nombre_norm):
        fecha_emision_doc = "05/11/2026"
        numero_completo = "B001 - 762842"
        serie = "B001"
        tipo_doc_nombre = "BOLETA DE VENTA ELECTRÓNICA"

        emisor = {
            "ruc": "20547896321",
            "razon_social": "Comercial Andina S.A.C.",
            "nombre_comercial": "Comercial Andina S.A.C.",
            "tienda_sede": "Pisco",
            "direccion_fiscal": "Av. Mariscal Benavides N° 245 Chincha - Ica",
            "confianza": 99.4,
        }

        cliente = {
            "tipo_documento": "DNI",
            "numero_documento": "00000000",
            "nombre_completo": "Cliente Final",
            "usuario_formulario": usuario or "Luis Alcala",
            "confianza": 98.0,
        }

        items = [
            {
                "codigo": "UT-01",
                "descripcion": "Cuaderno universitario",
                "unidad": "NIU",
                "cantidad": 1,
                "precio_unitario": 12.00,
                "valor_venta": 12.00,
                "confianza": 99.2,
            },
            {
                "codigo": "UT-02",
                "descripcion": "Lapicero azul",
                "unidad": "NIU",
                "cantidad": 2,
                "precio_unitario": 2.50,
                "valor_venta": 5.00,
                "confianza": 99.0,
            },
            {
                "codigo": "UT-03",
                "descripcion": "Archivador A4",
                "unidad": "NIU",
                "cantidad": 1,
                "precio_unitario": 18.00,
                "valor_venta": 18.00,
                "confianza": 99.3,
            },
        ]

        subtotal = 35.00
        igv = 6.30
        total = 41.30
        monto_en_letras = "Cuarenta y uno con 30/100 soles"

        lineas_texto = [
            "Comercial Andina S.A.C.",
            "RUC: 20547896321 - Av. Mariscal Benavides N° 245 Chincha - Ica",
            "BOLETA DE VENTA ELECTRÓNICA B001 - 762842",
            "Fecha de emisión: 05/11/2026",
            "Cliente: Cliente Final (DNI: 00000000)",
            "1 Cuaderno universitario S/ 12.00 S/ 12.00",
            "2 Lapicero azul S/ 2.50 S/ 5.00",
            "1 Archivador A4 S/ 18.00 S/ 18.00",
            "Subtotal: S/ 35.00",
            "IGV (18%): S/ 6.30",
            "Total: S/ 41.30",
        ]

    # =========================================================================
    # CASO 4: BOLETA ELECTRÓNICA - COMERCIAL ANDINA CHINCHA
    # Archivo: Boleta_electronica_-UtilesE_Comercial_Andina_Chincha.png
    # Total visible: S/ 95.00 | Número: B001 - 762841 | Fecha: 04/11/2026
    # =========================================================================
    elif "utilese" in nombre_norm and "boleta" in nombre_norm:
        fecha_emision_doc = "04/11/2026"
        numero_completo = "B001 - 762841"
        serie = "B001"
        tipo_doc_nombre = "BOLETA DE VENTA ELECTRÓNICA"

        emisor = {
            "ruc": "20547896321",
            "razon_social": "Comercial Andina S.A.C.",
            "nombre_comercial": "Comercial Andina S.A.C.",
            "tienda_sede": "Chincha",
            "direccion_fiscal": "Av. Mariscal Benavides N° 245 Chincha - Ica",
            "confianza": 99.4,
        }

        cliente = {
            "tipo_documento": "DNI",
            "numero_documento": "00000000",
            "nombre_completo": "Cliente Final",
            "usuario_formulario": usuario or "Luis Alcala",
            "confianza": 98.0,
        }

        items = [
            {
                "codigo": "UT-11",
                "descripcion": "Cuaderno A4",
                "unidad": "NIU",
                "cantidad": 2,
                "precio_unitario": 15.00,
                "valor_venta": 30.00,
                "confianza": 99.1,
            },
            {
                "codigo": "UT-12",
                "descripcion": "Lapicero (caja)",
                "unidad": "NIU",
                "cantidad": 1,
                "precio_unitario": 25.00,
                "valor_venta": 25.00,
                "confianza": 98.9,
            },
            {
                "codigo": "UT-13",
                "descripcion": "Resaltador (set)",
                "unidad": "NIU",
                "cantidad": 1,
                "precio_unitario": 40.00,
                "valor_venta": 40.00,
                "confianza": 99.2,
            },
        ]

        subtotal = 80.51
        igv = 14.49
        total = 95.00
        monto_en_letras = "Noventa y cinco con 00/100 soles"

        lineas_texto = [
            "Comercial Andina S.A.C.",
            "RUC: 20547896321 - Av. Mariscal Benavides N° 245 Chincha - Ica",
            "BOLETA DE VENTA ELECTRÓNICA B001 - 762841",
            "Fecha de emisión: 04/11/2026",
            "Cliente: Cliente Final (DNI: 00000000)",
            "2 Cuaderno A4 S/ 15.00 S/ 30.00",
            "1 Lapicero (caja) S/ 25.00 S/ 25.00",
            "1 Resaltador (set) S/ 40.00 S/ 40.00",
            "Subtotal: S/ 80.51",
            "IGV (18%): S/ 14.49",
            "Total: S/ 95.00",
        ]

    # =========================================================================
    # CASO 5: FACTURA ELECTRÓNICA - COMERCIAL ANDINA CHINCHA
    # Archivo: Factura_Electronica-Utiles_Es_Comercial_Andina_Chincha.png
    # Total visible: S/ 382.32 | Número: F001 - 003567 | Fecha: 05/11/2026
    # =========================================================================
    elif "andina" in nombre_norm and "factura" in nombre_norm:
        fecha_emision_doc = "05/11/2026"
        numero_completo = "F001 - 003567"
        serie = "F001"
        tipo_doc_nombre = "FACTURA ELECTRÓNICA"

        emisor = {
            "ruc": "20547896321",
            "razon_social": "Comercial Andina S.A.C.",
            "nombre_comercial": "Comercial Andina S.A.C.",
            "tienda_sede": "Chincha",
            "direccion_fiscal": "Av. Mariscal Benavides N° 245 Chincha - Ica",
            "confianza": 99.5,
        }

        cliente = {
            "tipo_documento": "RUC",
            "numero_documento": "20609876543",
            "razon_social": "Servicios Logísticos del Sur S.A.C.",
            "direccion": "Av. Los Industriales N° 780 - Pisco",
            "usuario_formulario": usuario or "Luis Alcala",
            "confianza": 98.7,
        }

        items = [
            {
                "codigo": "UT-21",
                "descripcion": "Papel bond A4 (caja)",
                "unidad": "NIU",
                "cantidad": 3,
                "precio_unitario": 28.00,
                "valor_venta": 84.00,
                "confianza": 99.3,
            },
            {
                "codigo": "UT-22",
                "descripcion": "Tóner para impresora",
                "unidad": "NIU",
                "cantidad": 2,
                "precio_unitario": 120.00,
                "valor_venta": 240.00,
                "confianza": 99.5,
            },
        ]

        subtotal = 324.00
        igv = 58.32
        total = 382.32
        monto_en_letras = "Trescientos ochenta y dos con 32/100 soles"

        lineas_texto = [
            "Comercial Andina S.A.C.",
            "RUC: 20547896321 - Av. Mariscal Benavides N° 245 Chincha - Ica",
            "FACTURA ELECTRÓNICA F001 - 003567",
            "Fecha de emisión: 05/11/2026",
            "Cliente: Servicios Logísticos del Sur S.A.C. RUC: 20609876543",
            "3 Papel bond A4 (caja) 28.00 84.00",
            "2 Tóner para impresora 120.00 240.00",
            "Subtotal: S/ 324.00",
            "IGV (18%): S/ 58.32",
            "Total: S/ 382.32",
        ]

    # =========================================================================
    # CASO GENÉRICO / FALLBACK
    # =========================================================================
    else:
        es_factura = tipo_norm == "factura"
        serie = "F001" if es_factura else "B001"
        numero_completo = generar_correlativo(f"{nombre_archivo}-{fecha or ahora_utc}", serie)
        fecha_emision_doc = fecha or datetime.now().strftime("%Y-%m-%d")
        tipo_doc_nombre = "FACTURA ELECTRÓNICA" if es_factura else "BOLETA DE VENTA ELECTRÓNICA"

        sedes_direcciones = {
            "Chincha": "Av. Mariscal Benavides 450, Chincha Alta, Ica",
            "Pisco": "Calle San Martín 210, Pisco, Ica",
            "Ica": "Av. San Martín 880, Cercado de Ica, Ica",
        }
        direccion_emisor = sedes_direcciones.get(tienda_norm, f"Sede {tienda_norm}, Ica, Perú")

        emisor = {
            "ruc": "20601845923",
            "razon_social": "DISTRIBUIDORA Y COMERCIAL DEL SUR S.A.C.",
            "nombre_comercial": f"COMERCIAL SUR {tienda_norm.upper()}",
            "tienda_sede": tienda_norm,
            "direccion_fiscal": direccion_emisor,
            "telefono": "(056) 215480",
            "confianza": 98.5,
        }

        if es_factura:
            cliente = {
                "tipo_documento": "RUC",
                "numero_documento": "20547896321",
                "razon_social": f"CORPORACIÓN REGIONAL {tienda_norm.upper()} S.A.C.",
                "usuario_formulario": usuario or "Luis Alcala",
                "confianza": 97.5,
            }
            items = [
                {
                    "codigo": "PRD-101",
                    "descripcion": f"Material operativo sede {tienda_norm}",
                    "unidad": "NIU",
                    "cantidad": 2,
                    "precio_unitario": 125.00,
                    "valor_venta": 250.00,
                    "confianza": 98.8,
                },
                {
                    "codigo": "SRV-204",
                    "descripcion": "Servicio logístico local",
                    "unidad": "ZZ",
                    "cantidad": 1,
                    "precio_unitario": 150.00,
                    "valor_venta": 150.00,
                    "confianza": 98.5,
                },
            ]
            subtotal = 400.00
            igv = 72.00
            total = 472.00
            monto_en_letras = "CUATROCIENTOS SETENTA Y DOS CON 00/100 SOLES"
        else:
            cliente = {
                "tipo_documento": "DNI",
                "numero_documento": "47852369",
                "nombre_completo": usuario or "CLIENTE REGISTRADO",
                "usuario_formulario": usuario or "Luis Alcala",
                "confianza": 97.0,
            }
            items = [
                {
                    "codigo": "ART-01",
                    "descripcion": f"Suministros varios sede {tienda_norm}",
                    "unidad": "NIU",
                    "cantidad": 1,
                    "precio_unitario": 95.00,
                    "valor_venta": 95.00,
                    "confianza": 98.2,
                }
            ]
            subtotal = 80.51
            igv = 14.49
            total = 95.00
            monto_en_letras = "NOVENTA Y CINCO CON 00/100 SOLES"

        lineas_texto = [
            emisor["razon_social"],
            f"RUC: {emisor['ruc']} - Sede {tienda_norm}",
            f"{tipo_doc_nombre}: {numero_completo}",
            f"FECHA EMISIÓN: {fecha_emision_doc}",
            f"TOTAL: S/ {total:.2f}",
        ]

    # Construcción consolidada del JSON de Textract
    return {
        "metadatos_extraccion": {
            "servicio": "Amazon Textract (Simulación Floci)",
            "es_simulado": True,
            "version_motor": "v2.0-verified-mock",
            "fecha_procesamiento": ahora_utc,
            "archivo_analizado": nombre_archivo,
            "confianza_general": 99.1,
            "nota_academica": "Extracción generada por simulación local para entorno Floci basada en los comprobantes de prueba.",
        },
        "metadatos_formulario": {
            "fecha_registro_formulario": fecha or datetime.now().strftime("%Y-%m-%d"),
            "usuario_operador": usuario or "Luis Alcala",
            "tienda_sede_formulario": tienda_norm,
            "observacion_formulario": observacion or "Sin observaciones",
        },
        "comprobante": {
            "tipo": tipo_doc_nombre,
            "serie": serie,
            "numero_completo": numero_completo,
            "fecha_emision": fecha_emision_doc,
            "moneda": "PEN",
            "simbolo_moneda": "S/",
            "forma_pago": "Contado",
            "tienda_registrada": tienda_norm,
            "observacion_registrada": observacion or "Sin observaciones",
        },
        "emisor": emisor,
        "cliente": cliente,
        "items": items,
        "importes": {
            "subtotal": subtotal,
            "tasa_igv_porcentaje": 18.0,
            "igv": igv,
            "total": total,
            "monto_en_letras": monto_en_letras,
            "confianza": 99.2,
        },
        "lineas_texto_detectadas": lineas_texto,
    }
