"""
Script de prueba para generar PDF de ejemplo

Uso:
    python test_generate_pdf.py

Genera un PDF de prueba con datos de ejemplo e imágenes placeholder
"""
import requests
import json
from pathlib import Path
from PIL import Image
import io


def create_sample_image(width=800, height=600, color=(100, 150, 200), text="Sample"):
    """Crea una imagen de prueba"""
    img = Image.new('RGB', (width, height), color=color)
    return img


def image_to_bytes(img):
    """Convierte PIL Image a bytes"""
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return buffer.getvalue()


def test_pdf_generation(api_url="http://localhost:8000"):
    """
    Prueba la generación de PDF con datos de ejemplo
    """
    print("🧪 Iniciando prueba de generación de PDF...")
    print(f"📡 API URL: {api_url}")
    
    # 1. Datos de ejemplo
    data = {
        "nombre_planta": "Planta Solar Querétaro - Prueba",
        "id_proyecto": "TEST001",
        "ubicacion": "Querétaro, México",
        "persona_responsable_interna": "Sebastián Leocadio Domínguez",
        "responsable_obra": "Sebastián Leocadio Domínguez",
        "numero_visita": 1,
        "hora_entrada": "09:00",
        "hora_salida": "11:30",
        "motivo_visita": "Prueba del sistema de generación de PDFs",
        "avances_conforme_cronograma": True,
        "razon_no_conforme": "",
        "acuerdos": "Validar funcionalidad del sistema y calidad del PDF generado",
        "lugar_elaboracion": "Querétaro, Qro."
    }
    
    print(f"✅ Datos preparados: {data['nombre_planta']}")
    
    # 2. Crear imágenes de prueba
    print("🖼️  Generando 12 imágenes de prueba...")
    images = []
    colors = [
        (100, 150, 200),  # Azul
        (150, 100, 200),  # Morado
        (200, 150, 100),  # Naranja
        (100, 200, 150),  # Verde
        (200, 100, 150),  # Rosa
        (150, 200, 100),  # Verde claro
    ]
    
    for i in range(12):
        color = colors[i % len(colors)]
        img = create_sample_image(
            width=1200,
            height=900,
            color=color,
            text=f"Foto {i+1}"
        )
        img_bytes = image_to_bytes(img)
        images.append(('images', (f'foto_{i+1}.jpg', img_bytes, 'image/jpeg')))
    
    print(f"✅ {len(images)} imágenes creadas")
    
    # 3. Hacer request a la API
    print("📤 Enviando request a la API...")
    
    try:
        response = requests.post(
            f"{api_url}/api/reports/site-visit",
            data={'data': json.dumps(data)},
            files=images,
            timeout=60
        )
        
        # 4. Verificar respuesta
        if response.status_code == 200:
            print("✅ PDF generado exitosamente!")
            
            # Extraer metadata de headers
            pdf_size = response.headers.get('X-PDF-Size', 'unknown')
            images_count = response.headers.get('X-Images-Processed', 'unknown')
            compression = response.headers.get('X-Compression-Ratio', 'unknown')
            
            print(f"📊 Metadata del PDF:")
            print(f"   - Tamaño: {int(pdf_size) / 1024 / 1024:.2f} MB")
            print(f"   - Imágenes procesadas: {images_count}")
            print(f"   - Ratio de compresión: {compression}x")
            
            # 5. Guardar PDF
            output_path = Path("test_output")
            output_path.mkdir(exist_ok=True)
            
            pdf_filename = output_path / "reporte_prueba.pdf"
            with open(pdf_filename, 'wb') as f:
                f.write(response.content)
            
            pdf_filename_abs = pdf_filename.absolute()
            print(f"💾 PDF guardado en: {pdf_filename_abs}")
            print(f"📂 Abrir con: {pdf_filename_abs}")
            
            return True
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo:")
        print("   - Con Docker: docker-compose up")
        print("   - Sin Docker: python main.py")
        return False
    
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False


def test_health_check(api_url="http://localhost:8000"):
    """Verifica que el servicio esté disponible"""
    print("🏥 Verificando salud del servicio...")
    
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servicio operacional: {data['service']}")
            return True
        else:
            print(f"⚠️  Servicio respondió con código: {response.status_code}")
            return False
    except:
        print("❌ Servicio no disponible")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TEST DE GENERACIÓN DE PDF")
    print("=" * 60)
    print()
    
    # Verificar que el servicio esté corriendo
    if test_health_check():
        print()
        # Ejecutar prueba de generación
        success = test_pdf_generation()
        print()
        
        if success:
            print("=" * 60)
            print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
            print("=" * 60)
        else:
            print("=" * 60)
            print("❌ PRUEBA FALLÓ")
            print("=" * 60)
    else:
        print()
        print("❌ No se puede ejecutar la prueba porque el servicio no está disponible")
        print()
        print("🚀 Para iniciar el servicio:")
        print("   Con Docker: docker-compose up")
        print("   Sin Docker: python main.py")
