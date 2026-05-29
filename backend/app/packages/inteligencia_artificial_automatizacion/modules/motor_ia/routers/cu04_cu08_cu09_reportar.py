"""
CU04 — Reportar Emergencia
CU08 — Clasificación Automática de Incidentes (IA / Whisper + OpenRouter)
CU09 — Priorización de Emergencias (IA)

POST /emergencias/analizar-audio → CU08/CU09 Pre-análisis con IA antes de reportar
POST /emergencias/reportar       → CU04 Reportar emergencia vehicular
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import uuid
import shutil

from app.db.session import get_db
from app.core.dependencies import require_role
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.emergencia import EmergenciaCreate, EmergenciaOut
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.schemas.ai_schemas import AnalisisEstructuradoIA
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.prioridad import Prioridad
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.categoria_problema import CategoriaProblema
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.services import emergencia_service
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.services.ai_service import analizar_transcripcion_whisper
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.services.transcripcion_service import transcribir_audio_local

router = APIRouter(prefix="/emergencias", tags=["IA — Reportar / Clasificar / Priorizar (CU04/CU08/CU09)"])

@router.post(
    "/analizar-audio",
    response_model=AnalisisEstructuradoIA,
    summary="CU08/CU09 — Clasificar y priorizar emergencia con IA (pre-reporte)",
)
async def analizar_audio_ia(
    archivo_audio: Optional[UploadFile] = File(None, description="Audio del cliente (opcional)"),
    texto_escrito: Optional[str] = Form(None, description="Descripción escrita del cliente (opcional)"),
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    """
    1. Transcribe el audio con Whisper Local (si existe).
    2. Combina con el texto escrito (si existe).
    3. Clasifica el tipo de problema (CU08) con OpenRouter IA.
    4. Asigna una prioridad automática (CU09) según criticidad.
    """
    if not archivo_audio and not texto_escrito:
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos un audio o una descripción escrita.")

    try:
        texto_crudo = ""
        if archivo_audio:
            texto_crudo = await transcribir_audio_local(archivo_audio)
        
        if texto_escrito:
            if texto_crudo:
                texto_crudo = f"{texto_crudo}. Descripción adicional: {texto_escrito}"
            else:
                texto_crudo = texto_escrito

        cats_res = await db.execute(select(CategoriaProblema.id, CategoriaProblema.descripcion))
        prios_res = await db.execute(select(Prioridad.id, Prioridad.descripcion))
        categorias_activas = [{"id": r.id, "nombre": r.descripcion} for r in cats_res.all()]
        prioridades_activas = [{"id": r.id, "nombre": r.descripcion} for r in prios_res.all()]

        return await analizar_transcripcion_whisper(
            texto_crudo=texto_crudo,
            categorias_disponibles=categorias_activas,
            prioridades_disponibles=prioridades_activas,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en procesamiento IA: {str(e)}")


@router.post(
    "/upload-multimedia",
    summary="Subir evidencias estáticas y transcribir audio",
)
async def upload_multimedia(
    files: List[UploadFile] = File(...),
    current=Depends(require_role("cliente")),
):
    """
    Guarda los archivos (Evidencias/Audio) permanentemente en disco.
    Si detecta un audio, invoca a Whisper para retornar su transcripción cruda asíncronamente.
    """
    UPLOAD_DIR = "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    urls = []
    transcripcion = None
    
    for file in files:
        # Generar nombre único
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        
        # Escribir a disco permanentemente
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_url = f"/uploads/{unique_name}"
        urls.append({"filename": file.filename, "url": file_url})
        
        # Si es audio, lo transcribimos al vuelo con Whisper
        mime = file.content_type or ""
        if "audio" in mime or ext.lower() in ['mp3', 'wav', 'm4a', 'aac', 'ogg']:
            try:
                # transcribir_audio_local espera un UploadFile, simulamos rebobinando
                await file.seek(0)
                transcripcion = await transcribir_audio_local(file)
            except Exception as e:
                print(f"Advertencia: falló whisper al transcribir archivo subido: {e}")

    return {
        "archivos": urls,
        "transcripcion_cruda": transcripcion
    }




# ─── CU04: Reportar Emergencia ────────────────────────────────────────────────

@router.post(
    "/reportar",
    response_model=EmergenciaOut,
    status_code=201,
    summary="CU04 — Reportar emergencia vehicular",
)
async def reportar(
    data: EmergenciaCreate,
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    """
    El cliente envía los datos de la emergencia (ya clasificada por IA).
    El motor de asignación (CU11) selecciona automáticamente el taller más cercano.
    """
    print(f"[Endpoint] Reportar emergencia: {data.placaVehiculo}, texto={data.texto_adicional}, fotos={len(data.evidencias_urls)}")
    return await emergencia_service.reportar_emergencia(data, current["user_id"], db)


@router.get("/{emergencia_id}", response_model=EmergenciaOut)
async def obtener_emergencia(
    emergencia_id: int,
    current=Depends(require_role("cliente", "taller")),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtener detalles de una emergencia específica.
    """
    return await emergencia_service.obtener_emergencia_por_id(emergencia_id, db)


@router.put("/{emergencia_id}", response_model=EmergenciaOut)
async def actualizar_emergencia(
    emergencia_id: int,
    data: EmergenciaCreate,
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    """
    Permite al cliente corregir un reporte rechazado por la IA o actualizar datos.
    """
    print(f"🔄 [Endpoint] Corregir emergencia {emergencia_id}: texto={data.texto_adicional}, fotos={len(data.evidencias_urls)}")
    return await emergencia_service.actualizar_emergencia(emergencia_id, data, current["user_id"], db)


@router.delete("/{emergencia_id}")
async def cancelar_emergencia(
    emergencia_id: int,
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancela una emergencia que aún no ha sido aceptada por un taller.
    """
    return await emergencia_service.cancelar_emergencia(emergencia_id, current["user_id"], db)
