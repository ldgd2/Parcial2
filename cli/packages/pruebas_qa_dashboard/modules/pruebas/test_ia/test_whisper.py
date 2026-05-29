import sys
import os

# Agregamos la ruta base del backend para poder importar los módulos libremente
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

import asyncio
try:
    from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.services.transcripcion_service import transcribir_audio_local
except ImportError:
    print("[ERROR] No se pudo importar los servicios de IA. Asegúrate de estar corriendo esto desde la raíz.")
    sys.exit(1)

# Simulamos la estructura de un UploadFile de FastAPI
class DummyUploadFile:
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, 'rb')
        
    async def read(self, size=-1):
        # file.read es sincronico localmente pero FastAPI usa su wrapper asíncrono,
        # aqui lo emulamos asíncrono para no romper la compatibilidad con transcribir_audio_local.
        await asyncio.sleep(0.01)
        return self.file.read(size)
        
    async def seek(self, offset):
        self.file.seek(offset)

async def test_transcripcion():
    print("Iniciando prueba local de Whisper...")
    # Crear un archivo wav temporal ficticio por si no hay audios
    test_audio = "test_audio_emergencia.wav"
    if not os.path.exists(test_audio):
        print(f"[!] No existe {test_audio}. Por favor arrastra un mini audio de prueba aquí.")
        print("Para efectos de inicialización, instanciando el modelo...")
        from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.services.transcripcion_service import get_whisper_model
        get_whisper_model()
        print("[OK] Modelo de Whisper cargado exitosamente en ram.")
        return

    dummy_file = DummyUploadFile(test_audio)
    try:
        resultado = await transcribir_audio_local(dummy_file)
        print("\n--- TRANSCRIPCIÓN ---")
        print(resultado)
        print("---------------------")
    except Exception as e:
        print(f"Error en la prueba de whisper: {e}")
    finally:
        dummy_file.file.close()

if __name__ == "__main__":
    asyncio.run(test_transcripcion())
