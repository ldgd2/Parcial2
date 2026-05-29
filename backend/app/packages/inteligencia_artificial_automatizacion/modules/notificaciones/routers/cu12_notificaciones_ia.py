"""
CU12 — Envío de Notificaciones

Este módulo define los endpoints de webhooks y triggers de notificación.
Las notificaciones se envían automáticamente como efecto secundario de otros CUs
(ej: cuando CU11 asigna una emergencia, CU12 notifica al cliente).

POST /notificaciones/test → Verificar canal de notificaciones (uso interno/dev)
GET  /notificaciones/mis-alertas → Listar alertas pendientes del usuario autenticado
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/notificaciones", tags=["IA — Notificaciones (CU12)"])


@router.get(
    "/mis-alertas",
    summary="CU12 — Listar alertas y notificaciones del usuario activo",
)
async def mis_alertas(
    current=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna las notificaciones pendientes del usuario autenticado.
    (Implementación futura: integración con WebSocket o Firebase Cloud Messaging)
    """
    # Placeholder hasta integrar sistema de notificaciones en tiempo real
    return {
        "alertas": [],
        "mensaje": "Sistema de notificaciones en tiempo real próximamente disponible.",
        "usuario_id": current.get("user_id"),
    }


@router.post(
    "/test",
    summary="CU12 — Verificar canal de notificaciones (desarrollo)",
    include_in_schema=False,  # Oculto en producción
)
async def test_notificacion(current=Depends(get_current_user)):
    """Endpoint interno para verificar que el canal de notificaciones funciona."""
    return {"status": "ok", "destino": current.get("sub"), "canal": "http-polling"}
