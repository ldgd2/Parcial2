from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import os
import uuid

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.schemas.chat import MensajeChatCreate, MensajeChatOut
from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.services import chat_service

router = APIRouter(prefix="/chat", tags=["Comercio — Chat (CU16)"])

@router.get("/{emergencia_id}", response_model=list[MensajeChatOut])
async def get_chat_history(
    emergencia_id: int,
    db: AsyncSession = Depends(get_db),
    current = Depends(get_current_user)
):
    return await chat_service.obtener_historial(emergencia_id, db)

@router.post("/{emergencia_id}", response_model=MensajeChatOut)
async def send_message(
    emergencia_id: int,
    data: MensajeChatCreate,
    db: AsyncSession = Depends(get_db),
    current = Depends(get_current_user)
):
    # 'current' es un dict con 'user_id' y 'role' (del dependencie require_role o get_current_user)
    # Nota: get_current_user devuelve un dict con 'user_id', 'role', etc.
    return await chat_service.enviar_mensaje(
        emergencia_id=emergencia_id,
        data=data,
        remitente_id=current["user_id"],
        rol=current["role"],
        db=db
    )

@router.post("/{emergencia_id}/upload_media", response_model=MensajeChatOut)
async def upload_chat_media(
    emergencia_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current = Depends(get_current_user)
):
    # Crear directorio estructurado: uploads/emergencias/{emergencia_id}/chat/
    upload_dir = os.path.join("uploads", "emergencias", str(emergencia_id), "chat")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Guardar archivo
    file_ext = os.path.splitext(file.filename)[1].lower()
    file_name = f"chat_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, file_name)
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # La ruta relativa para el frontend/DB será usando '/' para compatibilidad web
    relative_url = f"uploads/emergencias/{emergencia_id}/chat/{file_name}"
    
    # Determinar tipo de archivo (audio o imagen)
    audio_extensions = [".mp3", ".wav", ".m4a", ".ogg", ".aac", ".webm"]
    if file_ext in audio_extensions:
        data = MensajeChatCreate(audio_url=relative_url)
    else:
        # Por defecto asumimos que el resto de archivos subidos aquí son imágenes
        data = MensajeChatCreate(imagen_url=relative_url)
        
    return await chat_service.enviar_mensaje(
        emergencia_id=emergencia_id,
        data=data,
        remitente_id=current["user_id"],
        rol=current["role"],
        db=db
    )
