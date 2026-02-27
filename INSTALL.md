# 🛠️ Guía de Instalación

Esta guía detalla cómo configurar y ejecutar el servicio de generación de PDF en tu entorno local.

## 📋 Requisitos Previos

### Para desarrollo con Docker (Recomendado)
- **Docker Desktop** (Windows/Mac) o **Docker Engine** (Linux)
- **Git**

### Para desarrollo sin Docker (Solo usuarios avanzados)
- Python 3.11+
- GTK3 Runtime (necesario para WeasyPrint en Windows)
- Dependencias del sistema adicionales (libpango, etc.)

---

## 🚀 Opción A: Instalación con Docker (Recomendado)

Esta es la forma más sencilla de asegurar que todas las dependencias (incluyendo WeasyPrint y sus librerías gráficas) funcionen correctamente.

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd pdf-generator-service
```

### 2. Configurar variables de entorno

Copia el archivo de ejemplo y ajústalo si es necesario:

```bash
# En Windows (PowerShell)
copy .env.example .env

# En Linux/Mac
cp .env.example .env
```

### 3. Construir y ejecutar

```bash
docker-compose up --build
```

El servicio estará disponible en:
- API: `http://localhost:8000`
- Documentación Interactiva: `http://localhost:8000/docs`

---

## 🐍 Opción B: Instalación Manual con Python

⚠️ **Nota para usuarios de Windows:** Instalar WeasyPrint directamente en Windows puede ser complicado debido a las dependencias de GTK. Se recomienda encarecidamente usar Docker o WSL2.

### 1. Crear entorno virtual

```bash
python -m venv venv
```

### 2. Activar entorno virtual

- **Windows:** `.\venv\Scripts\activate`
- **Linux/Mac:** `source venv/bin/activate`

### 3. Instalar dependencias GTK (Solo Windows)

1. Descargar e instalar el [GTK3 Runtime para Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer).
2. Asegurar que la ruta `bin` de GTK3 esté en tu PATH del sistema.

### 4. Instalar librerías de Python

```bash
pip install -r requirements.txt
```

### 5. Ejecutar el servidor

```bash
uvicorn main:app --reload
```

---

## ✅ Verificar Instalación

Para verificar que el servicio está funcionando correctamente, puedes ejecutar el script de prueba incluido:

```bash
# Asegúrate de tener el entorno activado o estar usando docker exec
python test_generate_pdf.py
```

Si todo funciona bien, se generará un archivo `test_output/reporte_prueba.pdf`.
