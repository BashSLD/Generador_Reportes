# 🚀 Guía Rápida de Despliegue

## ⚡ Opción 1: Deploy a Railway (RECOMENDADO)

### Paso 1: Preparar repositorio

```bash
# Inicializar Git si no lo has hecho
git init
git add .
git commit -m "Initial commit: PDF Generator Service"

# Crear repo en GitHub y subir
git remote add origin https://github.com/tu-usuario/pdf-generator-service.git
git push -u origin main
```

### Paso 2: Deploy en Railway

1. Ve a https://railway.app
2. Click en "New Project"
3. Selecciona "Deploy from GitHub repo"
4. Conecta tu cuenta de GitHub
5. Selecciona el repositorio `pdf-generator-service`
6. Railway detecta el Dockerfile automáticamente
7. Click en "Deploy"

**¡Listo!** En 2-3 minutos tu servicio estará en línea.

### Paso 3: Obtener URL del servicio

1. En Railway, ve a tu proyecto
2. Click en "Settings"
3. En "Domains", genera un dominio público
4. Tu URL será algo como: `https://pdf-generator-production-xxxx.up.railway.app`

### Paso 4: Configurar variables de entorno (opcional)

En Railway > Settings > Variables:

```
MAX_IMAGE_WIDTH=800
IMAGE_QUALITY=85
MAX_IMAGE_SIZE_MB=10
ENVIRONMENT=production
DEBUG=false
```

---

## 🏠 Opción 2: Probar Localmente con Docker

### Paso 1: Instalar Docker Desktop

**Windows/Mac:**
- Descargar de: https://www.docker.com/products/docker-desktop/
- Instalar (siguiente, siguiente, siguiente)
- Reiniciar PC si es necesario

### Paso 2: Ejecutar el servicio

```bash
# En el directorio del proyecto
docker-compose build --no-cache && docker-compose up

# Esperar a ver: "Application startup complete"
```

### Paso 3: Probar el servicio

```bash
# Abrir en navegador:
http://localhost:8000/docs

# O ejecutar el script de prueba:
python test_generate_pdf.py
```

---

## 📦 Opción 3: Sin Docker (Solo Railway)

Si no quieres instalar Docker localmente:

```bash
# 1. Hacer cambios en el código

# 2. Commit y push
git add .
git commit -m "Feature: cambio en template"
git push

# 3. Railway auto-deploya en 2 minutos
```

**Ventaja:** Cero configuración local
**Desventaja:** Ciclo de desarrollo más lento

---

## 🔗 Integrar con Core System

### Si ambos están en Railway:

```python
# En Core System
from integration_client import PDFGeneratorClient

# Usar nombre interno del servicio (sin HTTPS)
client = PDFGeneratorClient("http://pdf-service:8000")

pdf_bytes = await client.generate_site_visit_report(data, images)
```

### Si solo PDF service está en Railway:

```python
# En Core System (local o en otro servidor)
client = PDFGeneratorClient("https://tu-servicio.up.railway.app")

pdf_bytes = await client.generate_site_visit_report(data, images)
```

---

## 🧪 Verificar que funciona

### Test 1: Health check

```bash
curl https://tu-servicio.up.railway.app/health
```

Debe responder:
```json
{
  "status": "healthy",
  "service": "PDF Generator Service"
}
```

### Test 2: Generar PDF de prueba

```bash
# Ejecutar script de prueba
python test_generate_pdf.py

# Verificar que se creó test_output/reporte_prueba.pdf
```

---

## 🐛 Troubleshooting

### Railway: Build falla

**Problema:** "Cannot find Dockerfile"
**Solución:** Asegurarse de que `Dockerfile` está en el root del repo

### Railway: Servicio no responde

**Problema:** 502 Bad Gateway
**Solución:** 
- Ver logs en Railway Dashboard
- Verificar que el puerto es `$PORT` (Railway lo asigna automáticamente)

### Local: "Cannot connect to Docker daemon"

**Problema:** Docker Desktop no está corriendo
**Solución:** Iniciar Docker Desktop desde el menú de Windows

### Local: PDF se genera muy lento

**Esto es normal en Windows.** WeasyPrint es ~5x más lento en Windows.
En Railway (Linux) será rápido.

---

## 📊 Monitoreo

### Ver logs en Railway

1. Railway Dashboard > Tu proyecto
2. Click en "Deployments"
3. Click en el deployment activo
4. Ver "Logs" en tiempo real

### Métricas

Railway muestra automáticamente:
- CPU usage
- Memory usage
- Request count
- Response times

---

## 🔄 Actualizar el servicio

```bash
# 1. Hacer cambios en código
# 2. Commit
git add .
git commit -m "Update: descripción del cambio"

# 3. Push
git push

# Railway auto-deploya en ~2 minutos
```

---

## 💡 Tips

- **Desarrollo:** Usar Docker local para iterar rápido
- **Producción:** Railway maneja todo automáticamente
- **Staging:** Crear branch `staging` en Git, conectarlo a Railway como proyecto separado
- **Rollback:** En Railway, click en un deployment anterior y "Redeploy"

---

## 📞 Si algo no funciona

1. Verificar logs en Railway
2. Probar health check endpoint
3. Verificar variables de entorno