"""
CU14 — Gestión de Solicitud Cliente

GET /emergencias/mis-solicitudes → El cliente consulta el historial de sus emergencias reportadas

El cliente puede ver el estado de todas sus solicitudes de auxilio,
incluyendo el taller asignado y la evolución del servicio.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.dependencies import require_role
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.emergencia import EmergenciaOut
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.services import emergencia_service

router = APIRouter(prefix="/emergencias", tags=["Comercio — Solicitudes Cliente (CU14)"])


@router.get(
    "/mis-solicitudes",
    response_model=List[EmergenciaOut],
    summary="CU14 — Ver historial de mis solicitudes de auxilio",
)
async def mis_solicitudes(
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    """
    CU14: Gestión de Solicitud Cliente —
    Retorna todas las emergencias reportadas por el cliente autenticado,
    con su estado actual y taller asignado.
    """
    return await emergencia_service.listar_emergencias_cliente(current["user_id"], db)
