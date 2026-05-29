import os
import tempfile
from fastapi import UploadFile
from faster_whisper import WhisperModel
from app.core.config import settings

# Inicialización perezosa (Lazy loading) del modelo Whisper Local
# Solo se cargará en memoria la primera vez que se mande a llamar.
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        print(f"Cargando modelo Whisper ({settings.WHISPER_MODEL_SIZE}) en {settings.WHISPER_DEVICE}...")
        _whisper_model = WhisperModel(
            settings.WHISPER_MODEL_SIZE, 
            device=settings.WHISPER_DEVICE, 
            compute_type=settings.WHISPER_COMPUTE_TYPE
        )
    return _whisper_model

async def transcribir_audio_local(file: UploadFile) -> str:
    """
    Guarda temporalmente el archivo subido, utiliza faster-whisper para
    extraer el texto y luego borra el archivo temporal.
    """
    model = get_whisper_model()
    
    # Crear un archivo temporal
    # delete=False es necesario en Windows porque el archivo no puede ser leído
    # por un proceso externo o librería C mientras está abierto por el framework nativo python.
    fd, temp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    try:
        # Guardar el contenido del UploadFile al temporal
        with open(temp_path, "wb") as buffer:
            # Leer el archivo en chunks para no saturar memoria si es pesado
            while True:
                chunk = await file.read(1024 * 1024) # 1MB
                if not chunk:
                    break
                buffer.write(chunk)
                
        # Procesar la transcripción
        segments, info = model.transcribe(temp_path, beam_size=5)
        
        texto_completo = []
        for segment in segments:
            texto_completo.append(segment.text)
            
        return " ".join(texto_completo).strip()
        
    finally:
        # Volver al inicio el puntero del archivo para evitar problemas posteriores si se reutiliza
        await file.seek(0)
        # Limpieza obligatoria del archivo temporal
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"No se pudo eliminar el archivo temporal: {e}")
