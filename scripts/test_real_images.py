import requests
import json
from pathlib import Path

def test_with_real_pictures():
    api_url = "http://localhost:8000/api/reports/site-visit"
    
    # 1. Configura tus datos
    data = {
        "nombre_planta": "Mi Proyecto Personal",
        "id_proyecto": "PROY-001",
        "ubicacion": "Ciudad de México",
        "persona_responsable_interna": "Tu Nombre",
        "responsable_obra": "Ing. Residente",
        "numero_visita": 1,
        "hora_entrada": "08:00",
        "hora_salida": "10:00",
        "motivo_visita": "Inspección técnica de avance",
        "avances_conforme_cronograma": True,
        "acuerdos": "Todo en orden para la siguiente fase",
        "lugar_elaboracion": "Oficina Central",
        "fecha": "05/02/2026"
    }

    # 2. Selecciona tus fotos
    # Coloca tus fotos en una carpeta llamada 'mis_fotos'
    folder = Path("mis_fotos")
    image_files = []
    
    for img_path in folder.glob("*.jpg"): # Busca todos los JPG
        with open(img_path, 'rb') as image_file:
            image_bytes = image_file.read()
        image_files.append(
            ('images', (img_path.name, image_bytes, 'image/jpeg'))
        )

    if not image_files:
        print("❌ No encontré fotos en la carpeta 'mis_fotos'")
        return

    # 3. Envía la petición
    print(f"📤 Enviando {len(image_files)} fotos...")
    response = requests.post(
        api_url,
        data={'data': json.dumps(data)},
        files=image_files
    )

    if response.status_code == 200:
        with open("reporte_real.pdf", "wb") as f:
            f.write(response.content)
        print("✅ ¡Reporte generado! Revisa 'reporte_real.pdf'")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    test_with_real_pictures()
