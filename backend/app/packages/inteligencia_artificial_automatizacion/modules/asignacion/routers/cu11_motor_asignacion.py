"""
CU11 — Ejecución del Motor de Asignación
(+ Gestión de emergencias por el administrador del taller)

GET  /gestion-emergencia/disponibles     → CU11 Emergencias disponibles para reclamar
GET  /gestion-emergencia/asignadas       → CU11 Emergencias ya asignadas a este taller
GET  /gestion-emergencia/{id}            → Detalle completo de una emergencia
POST /gestion-emergencia/{id}/analizar   → CU11 Bloquear/reclamar emergencia temporalmente
POST /gestion-emergencia/{id}/asignar    → CU11 Confirmar asignación con técnicos
POST /gestion-emergencia/{id}/estado     → CU11 Actualizar estado de la emergencia
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel

from app.db.session import get_db
from app.core.dependencies import require_role
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.services import emergencia_service
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.emergencia import EmergenciaOut, ActualizarEstadoRequest

router = APIRouter(prefix="/gestion-emergencia", tags=["IA — Motor de Asignación (CU11)"])


class AsignarTecnicosRequest(BaseModel):
    tecnicos_ids: List[int]


# ─── CU11: Motor de Asignación ────────────────────────────────────────────────

@router.get(
    "/disponibles",
    response_model=List[EmergenciaOut],
    summary="CU11 — Listar emergencias disponibles para reclamar",
)
async def listar_disponibles(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    """Retorna las emergencias asignadas por el motor que aún no han sido reclamadas."""
    taller_cod = current_user.get("taller")
    if not taller_cod:
        raise HTTPException(status_code=400, detail="El usuario no tiene un taller asociado.")
    return await emergencia_service.listar_emergencias_disponibles(taller_cod, db)


@router.get(
    "/asignadas",
    response_model=List[EmergenciaOut],
    summary="CU11 — Listar emergencias asignadas a este taller",
)
async def listar_asignadas(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    taller_cod = current_user.get("taller")
    if not taller_cod:
        raise HTTPException(status_code=400, detail="El usuario no tiene un taller asociado.")
    return await emergencia_service.listar_emergencias_taller(taller_cod, db)


@router.get(
    "/{id}",
    response_model=EmergenciaOut,
    summary="CU11 — Detalle completo de una emergencia",
)
async def obtener_emergencia(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "tecnico", "cliente")),
):
    emergencia = await emergencia_service.obtener_emergencia_detalle(id, db)
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada.")
    return emergencia


@router.post(
    "/{id}/analizar",
    summary="CU11 — Reclamar/bloquear emergencia de forma temporal",
)
async def bloquear_emergencia(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    taller_cod = current_user.get("taller")
    return await emergencia_service.bloquear_emergencia_temporal(id, taller_cod, db)


@router.post(
    "/{id}/asignar",
    summary="CU11 — Confirmar asignación de técnicos a la emergencia",
)
async def confirmar_asignacion(
    id: int,
    data: AsignarTecnicosRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    taller_cod = current_user.get("taller")
    return await emergencia_service.asignar_emergencia_taller(id, taller_cod, data.tecnicos_ids, db)


@router.post(
    "/{id}/estado",
    summary="CU11 — Actualizar estado de una emergencia",
)
async def actualizar_estado(
    id: int,
    data: ActualizarEstadoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    taller_cod = current_user.get("taller")
    return await emergencia_service.actualizar_estado_emergencia(id, data, taller_cod, db)
