# 📄 PDF Generator Service

Servicio de generación de PDFs profesionales usando FastAPI + WeasyPrint.

## 🚀 Features

- ✅ Generación de PDFs con diseño profesional
- ✅ Optimización automática de imágenes (resize + compresión)
- ✅ Templates HTML/CSS personalizables
- ✅ API REST con FastAPI
- ✅ Validación de datos con Pydantic
- ✅ Docker ready para Railway
- ✅ Reducción de tamaño de archivos hasta 70%

## 📚 Documentación

- **[Instalación y Ejecución Local](INSTALL.md)**: Guía paso a paso para correr el proyecto.
- **[Despliegue](DEPLOY.md)**: Instrucciones para desplegar en Railway u otros servicios.

## 📖 Uso Rápido de la API

### Endpoint principal: Generar PDF de visita a obra

**POST** `/api/reports/site-visit`

**Ejemplo con cURL:**

```bash
curl -X POST "http://localhost:8000/api/reports/site-visit" \
  -F 'data={"nombre_planta":"Planta Solar","id_proyecto":"ABC123","numero_visita":1,"hora_entrada":"09:00","hora_salida":"11:00","motivo_visita":"Inspección","persona_responsable_interna":"Juan Pérez","responsable_obra":"María López","avances_conforme_cronograma":true}' \
  -F "images=@foto1.jpg" \
  -F "images=@foto2.jpg" \
  --output reporte.pdf
```

Para documentación completa de la API, ejecuta el servicio y visita `http://localhost:8000/docs`.

## 📁 Estructura del Proyecto

```
pdf-generator-service/
├── main.py                  # FastAPI app principal
├── config.py                # Configuración
├── models.py                # Modelos de datos
├── pdf_service.py           # Lógica de generación PDF
├── image_processor.py       # Optimización de imágenes
├── templates/               # Templates HTML/CSS
├── Dockerfile               # Configuración Docker
├── docker-compose.yml       # Docker Compose
└── requirements.txt         # Dependencias
```

## ⚙️ Configuración Básica

El servicio se configura mediante variables de entorno (archivo `.env`):

```bash
MAX_IMAGE_WIDTH=800          # Ancho máximo imágenes (px)
IMAGE_QUALITY=85             # Calidad JPEG (0-100)
MAX_IMAGE_SIZE_MB=10         # Tamaño máximo por imagen
```
