from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import require_role, get_current_user
from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.services.notification_service import NotificationService
from pydantic import BaseModel

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones (CU12)"])

class TokenRequest(BaseModel):
    token: str
    dispositivo: str = "android"

class CustomNotificationRequest(BaseModel):
    user_id: int
    titulo: str
    cuerpo: str

@router.post("/registrar-token")
async def registrar_token(
    data: TokenRequest,
    current=Depends(get_current_user), # Cualquier usuario autenticado
    db: AsyncSession = Depends(get_db)
):
    """Permite a la App registrar el token de Firebase del dispositivo actual."""
    await NotificationService.registrar_token(db, current["user_id"], data.token, data.dispositivo, current["role"])
    return {"message": "Token registrado correctamente"}

@router.post("/test-broadcast")
async def test_broadcast(
    titulo: str = "SISTEMA TALLER",
    cuerpo: str = "Esta es una notificación de prueba para todos.",
    data: dict = None
):
    """Prueba de envío masivo (Broadcast) vía tópicos. (Sin auth para pruebas CLI)"""
    await NotificationService.enviar_notificacion_topic("todos", titulo, cuerpo, data)
    return {"message": "Notificación enviada al tópico 'todos'"}

@router.post("/test-personalizada")
async def test_personalizada(
    data: CustomNotificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Envía una notificación a un usuario específico por su ID. (Sin auth para pruebas CLI)"""
    # Envolvemos los datos adicionales si existen en el request o los pasamos vacíos
    count = await NotificationService.enviar_notificacion_usuario(db, data.user_id, data.titulo, data.cuerpo)
    if count == 0:
        raise HTTPException(status_code=404, detail="El usuario no tiene dispositivos registrados.")
    return {"message": f"Notificación enviada a {count} dispositivos."}

@router.post("/test-token")
async def test_token(
    token: str,
    titulo: str = "TEST DIRECTO",
    cuerpo: str = "Prueba por token específico.",
    data: dict = None
):
    """Envía una notificación a un token de dispositivo específico."""
    await NotificationService.enviar_notificacion_directa(token, titulo, cuerpo, data)
    return {"message": "Notificación enviada al dispositivo"}
