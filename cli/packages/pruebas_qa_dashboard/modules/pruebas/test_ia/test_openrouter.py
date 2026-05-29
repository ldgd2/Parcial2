import sys
import os

# Agregamos la ruta base del backend para poder importar los módulos
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

import asyncio
import json
try:
    from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.services.ai_service import analizar_transcripcion_whisper
    from app.core._test_mocks import MOCK_CATEGORIAS, MOCK_PRIORIDADES
except ImportError as e:
    print(f"[ERROR] No se pudo importar los módulos de la aplicación: {e}")
    sys.exit(1)

async def test_openrouter():
    print("Iniciando prueba de Conexión a OpenRouter...")
    texto_prueba = "El carro reventó la llanta delantera, ocupamos un mecánico, estoy en medio de la carretera."
    
    cats = [
        {"id": 1, "nombre": "Falla de Motor"},
        {"id": 2, "nombre": "Llanta Ponchada / Ruedas"},
        {"id": 3, "nombre": "Batería / Eléctrico"}
    ]
    
    prios = [
        {"id": 1, "nombre": "BAJA - Sin Riesgo"},
        {"id": 2, "nombre": "MEDIA - Vehículo inmovilizado"},
        {"id": 3, "nombre": "ALTA - Riesgo de accidente"}
    ]

    print(f"Texto de entrada: {texto_prueba}")
    
    # --- Prueba de Visión Interactiva ---
    print("\n📸 ¿Deseas incluir imágenes para probar la visión? (s/n)")
    incluir_fotos = input(">> ").lower() == 's'
    evidencias = []
    
    if incluir_fotos:
        print("Ingresa las URLs de las imágenes separadas por comas (o deja vacío para usar una de prueba):")
        urls_raw = input(">> ").strip()
        if urls_raw:
            evidencias = [u.strip() for u in urls_raw.split(',')]
        else:
            # URL de prueba por defecto (una llanta pinchada de Google Images)
            evidencias = ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_xN8J9x3G1v9B6V-y6Dq_E9uH_fPZ-zW7xw&s"]
            print(f"Usando imagen de prueba: {evidencias[0]}")

    print("\nLlamando a la IA...")
    try:
        resultado = await analizar_transcripcion_whisper(
            texto_prueba, 
            cats, 
            prios, 
            vehiculo_info="Toyota Corolla 2022",
            evidencias_urls=evidencias
        )
        print("\n[OK] ¡La IA respondió exitosamente!")
        print(f">> Título: {resultado.titulo_emergencia}")
        print(f">> Resumen: {resultado.resumen_taller}")
        print(f">> Categoría Sugerida: {resultado.id_categoria}")
        print(f">> Prioridad Sugerida: {resultado.id_prioridad}")
        print(f">> Recomendaciones: {resultado.recomendaciones_taller}")
        print(f"\n>> Ficha Técnica Generada:")
        print(json.dumps(resultado.ficha_tecnica.model_dump(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"[ERROR] Hubo un fallo en la prueba: {e}")

if __name__ == "__main__":
    asyncio.run(test_openrouter())
