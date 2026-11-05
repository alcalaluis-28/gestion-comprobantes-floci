# 🧾 Sistema de Automatización y Gestión de Comprobantes

Aplicación web empresarial desarrollada con **Python**, **Flask**, **Bulma CSS** y **Boto3** para el registro, análisis OCR simulado y almacenamiento de comprobantes de pago (**boletas de venta** y **facturas electrónicas**) de las sedes regionales de **Chincha, Pisco e Ica**, utilizando servicios de AWS emulados localmente mediante **Floci** y Docker Desktop.

---

## 🏛️ Arquitectura del Sistema

El sistema utiliza una arquitectura basada en Python y servicios de almacenamiento de AWS.

### 🔄 Flujo de procesamiento

```text
             [ USUARIO ]
                  |
                  v
          [ NAVEGADOR WEB ]
              Bulma CSS
                  |
                  v
             [ FLASK API ]
                  |
                  v
       [ SIMULACIÓN TEXTRACT ]
          Generación de JSON
                  |
                  v
              [ AMAZON S3 ]
        Almacenamiento de imágenes
                  |
                  v
          [ AMAZON DYNAMODB ]
         Persistencia de registros
                  |
                  v
          [ PANEL DE RESULTADOS ]
```

### ⚙️ Descripción del procesamiento

1. **Recepción y validación:** el usuario completa el formulario con los datos del comprobante y adjunta una imagen JPG o PNG. Flask valida los campos obligatorios, la fecha, el tipo de comprobante, el usuario y la sede correspondiente.

2. **Análisis del comprobante:** se ejecuta una simulación del servicio Amazon Textract mediante Python, generando información estructurada en formato JSON.

3. **Almacenamiento de imágenes:** la imagen original se almacena en Amazon S3, utilizando una clave única generada mediante UUID.

4. **Persistencia de información:** los datos del formulario, la referencia de la imagen almacenada y el JSON generado se guardan en Amazon DynamoDB.

5. **Control de errores:** si ocurre un fallo durante el almacenamiento en DynamoDB después de subir la imagen, el sistema ejecuta una operación de compensación para eliminar el archivo de S3 y evitar imágenes huérfanas.

6. **Consulta de información:** los comprobantes registrados se muestran en una tabla que permite visualizar las imágenes, consultar los datos JSON y eliminar registros.

7. **Métricas dinámicas:** el panel calcula el total de comprobantes, las tiendas con registros y las imágenes asociadas, actualizando los indicadores cuando se registra o elimina información.

> **Nota:** Amazon Textract se implementa mediante una simulación desarrollada en Python. No se realiza una conexión con el servicio real de Amazon Textract.

---

## 🛠️ Tecnologías Utilizadas

| Componente | Tecnología |
|---|---|
| Lenguaje de programación | Python |
| Framework Backend | Flask 3.1 |
| Framework Frontend | Bulma CSS 1.0.2 |
| Interactividad | JavaScript (Fetch API) |
| SDK de AWS | Boto3 |
| Almacenamiento de objetos | Amazon S3 |
| Base de datos NoSQL | Amazon DynamoDB |
| Análisis de documentos | Simulación de Amazon Textract |
| Emulación de AWS | Floci |
| Contenedores | Docker Desktop |
| Entorno de ejecución | PowerShell |

---

## 🎨 Diseño de la Aplicación

La interfaz utiliza una combinación de colores naturales para ofrecer una experiencia visual moderna, organizada y profesional.

| Color | Código | Aplicación |
|---|---|---|
| 🟢 Verde bosque | `#1B3B2B` | Barra lateral y botones principales |
| 🌿 Verde salvia | `#8BA888` | Indicadores y elementos secundarios |
| 🟤 Beige | `#F4F0E8` | Fondos y contenedores |
| ⚪ Blanco cálido | `#FAF9F5` | Fondo principal y formularios |
| 🟠 Terracota suave | `#C85A32` | Acciones de eliminación y advertencias |

### 🖥️ Componentes principales

- Barra lateral de navegación.
- Panel de resumen rápido.
- Formulario de registro de comprobantes.
- Tabla de comprobantes registrados.
- Ventana de vista previa de imágenes.
- Ventana de visualización de información JSON.
- Confirmación de eliminación de registros.

---

## 📋 Funcionalidades del Sistema

### 📝 Registro de comprobantes

El formulario permite registrar:

- Tipo de comprobante: Boleta o Factura.
- Fecha de emisión.
- Nombre del usuario responsable.
- Tienda o sede: Chincha, Pisco e Ica.
- Observación opcional.
- Imagen del comprobante en formato JPG o PNG.

### 📂 Gestión de comprobantes

Cada registro dispone de tres operaciones:

1. **Ver imagen:** permite visualizar la imagen almacenada en Amazon S3.
2. **Ver datos:** permite consultar la información JSON generada por la simulación de Textract.
3. **Eliminar:** permite eliminar el registro de DynamoDB y su imagen correspondiente de S3, previa confirmación.

### 📊 Resumen rápido

El panel presenta indicadores calculados a partir de los registros almacenados:

- Total de comprobantes registrados.
- Cantidad de tiendas con comprobantes registrados.
- Total de imágenes asociadas a los registros.
- Distribución de comprobantes por sede: Chincha, Pisco e Ica.

Los indicadores se actualizan automáticamente al registrar o eliminar comprobantes.

---

## 📦 Requisitos Previos

Para ejecutar el proyecto se necesita:

1. Docker Desktop instalado y en ejecución.
2. Floci CLI instalado.
3. Python 3.10 o superior.
4. AWS CLI instalado.
5. Visual Studio Code.
6. PowerShell.

---

## 🚀 Instalación y Configuración

### 1️⃣ Iniciar Floci

Abrir PowerShell y ejecutar:

```powershell
floci start
```

Comprobar el estado del entorno:

```powershell
floci doctor
```

Floci debe encontrarse en ejecución y responder en el endpoint local:

```text
http://localhost.floci.io:4566
```

### 2️⃣ Crear el entorno virtual de Python

Desde la carpeta principal del proyecto:

```powershell
py -m venv .venv
```

Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```powershell
py -m pip install -r requirements.txt
```

### 3️⃣ Configurar las variables de entorno

Crear el archivo `.env` a partir de la plantilla:

```powershell
Copy-Item .env.example .env
```

Configuración local utilizada:

```ini
SECRET_KEY=dev-cambiar-esta-clave
AWS_ENDPOINT_URL=http://localhost.floci.io:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
AWS_S3_BUCKET=comprobantes-floci
DYNAMODB_TABLE=comprobantes
```

Las credenciales `test/test` corresponden exclusivamente al entorno local emulado de Floci y no son credenciales de una cuenta real de AWS.

### 4️⃣ Inicialización de los servicios

La aplicación cuenta con funciones de verificación y aprovisionamiento de los recursos necesarios.

Al iniciar Flask, se verifica la existencia de:

- **Bucket S3:** `comprobantes-floci`.
- **Tabla DynamoDB:** `comprobantes`.

Si los recursos no existen, se crean automáticamente.

La tabla DynamoDB utiliza `id` como clave primaria de tipo String.

### 5️⃣ Ejecutar la aplicación

Con Floci activo y el entorno virtual habilitado, ejecutar:

```powershell
py app.py
```

Acceder desde el navegador:

- **Aplicación web:** http://127.0.0.1:5000
- **Endpoint de salud:** http://127.0.0.1:5000/health

Para detener el servidor, utilizar `Ctrl + C` en PowerShell.

---

## 🔌 Especificación de la API REST

La aplicación implementa los siguientes endpoints:

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/` | Muestra la interfaz principal. |
| `GET` | `/health` | Verifica el estado de la aplicación. |
| `GET` | `/api/comprobantes` | Lista los comprobantes y devuelve las métricas. |
| `POST` | `/api/comprobantes` | Registra un comprobante y procesa su imagen. |
| `GET` | `/api/comprobantes/<id>/json` | Consulta los datos JSON del análisis simulado. |
| `GET` | `/api/comprobantes/<id>/imagen` | Recupera la imagen almacenada en S3. |
| `DELETE` | `/api/comprobantes/<id>` | Elimina el registro y su imagen asociada. |

---

## 📁 Estructura del Proyecto

```text
comprobantes-floci/
├── app.py                      # Servidor Flask, enrutamiento y API REST
├── config.py                   # Carga de variables de entorno y configuración AWS
├── requirements.txt            # Dependencias del proyecto (Flask, Boto3, dotenv)
├── .env                        # Configuración local de Floci (no versionada)
├── .env.example                # Plantilla de variables de entorno
├── .gitignore                  # Exclusiones de Git (.venv, .env, __pycache__)
├── README.md                   # Documentación técnica completa
├── services/                   # Capa de integración AWS / Floci
│   ├── __init__.py             # Exportación unificada de servicios
│   ├── s3_service.py           # Operaciones S3 (bucket, upload, download, delete)
│   ├── dynamodb_service.py     # Operaciones DynamoDB (tabla, CRUD, tipos Decimal)
│   └── textract_service.py     # Extracción simulada JSON de boletas y facturas
├── templates/                  # Vistas HTML con Jinja2
│   ├── base.html               # Estructura base (Bulma CSS, FontAwesome, Fuentes)
│   └── index.html              # Dashboard, Sidebar, Formulario, Tabla y Modales
└── static/                     # Recursos estáticos
    ├── css/
    │   └── styles.css          # Paleta verde bosque/salvia/beige y componentes
    └── js/
        └── app.js              # Lógica asíncrona, modales, métricas y Fetch API
```
---

## 🧪 Pruebas del Sistema

Durante el desarrollo se realizaron pruebas de integración utilizando Floci como entorno local de emulación de servicios AWS.

Las verificaciones contemplaron:

- Creación y comprobación del bucket S3.
- Creación y comprobación de la tabla DynamoDB.
- Subida, recuperación y eliminación de imágenes.
- Registro y consulta de comprobantes.
- Simulación del análisis de boletas y facturas.
- Generación y consulta de información JSON.
- Validación de formatos de imágenes.
- Visualización de comprobantes desde la interfaz.
- Eliminación coordinada entre S3 y DynamoDB.
- Actualización de indicadores dinámicos.
- Verificación del mecanismo de compensación ante fallos de persistencia.

Las pruebas de integración reportadas durante el desarrollo finalizaron satisfactoriamente, incluyendo ocho verificaciones del flujo principal de la aplicación.

---

## 🛡️ Seguridad y Buenas Prácticas

El proyecto contempla las siguientes medidas:

- Uso de credenciales de prueba para el entorno local de Floci.
- Separación de la configuración mediante variables de entorno.
- Exclusión del archivo `.env` y del entorno virtual `.venv` del repositorio Git.
- Validación de campos y archivos tanto en el frontend como en el backend.
- Restricción de imágenes a formatos JPG, JPEG y PNG.
- Generación de identificadores únicos mediante UUID.
- Manejo de errores durante el procesamiento y almacenamiento.
- Eliminación de imágenes de S3 cuando falla la persistencia correspondiente en DynamoDB.
- Recuperación de imágenes mediante el backend Flask, sin exponer credenciales al navegador.

> Para utilizar la aplicación fuera del entorno local de pruebas, se deben configurar credenciales, permisos y medidas de seguridad apropiadas para el entorno de despliegue.

---

## 🔗 Repositorio GitHub

**Nombre del proyecto:** Sistema de Automatización y Gestión de Comprobantes.

**Repositorio:**

https://github.com/alcalaluis-28/gestion-comprobantes-floci

---

<p align="center">
  **Sistema de Automatización y Gestión de Comprobantes**

  Desarrollado con Python, Flask y servicios AWS emulados mediante Floci.
</p>