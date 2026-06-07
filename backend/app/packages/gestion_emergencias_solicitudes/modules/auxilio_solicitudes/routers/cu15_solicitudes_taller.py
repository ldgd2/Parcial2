"""
CU15 — Gestión de Solicitud Taller

GET   /talleres/{cod}/solicitudes             → Ver historial de solicitudes del taller
PATCH /talleres/solicitudes/{id}/estado       → Actualizar estado de una emergencia

El taller puede ver todas las solicitudes que tiene asignadas y actualizar
su estado a lo largo del ciclo de vida del servicio.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.dependencies import require_role
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.emergencia import EmergenciaOut, ActualizarEstadoRequest
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.services import emergencia_service

router = APIRouter(prefix="/talleres", tags=["Comercio — Solicitudes Taller (CU15)"])


@router.get(
    "/{cod}/solicitudes",
    response_model=list[EmergenciaOut],
    summary="CU15 — Ver historial de solicitudes asignadas al taller",
)
async def solicitudes_taller(
    cod: str,
    current=Depends(require_role("tecnico", "admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    """
    CU15: Gestión de Solicitud Taller —
    Retorna todas las emergencias asignadas al taller en cualquier estado.
    """
    return await emergencia_service.listar_emergencias_taller(cod, db)


@router.patch(
    "/solicitudes/{emergencia_id}/estado",
    summary="CU15 — Actualizar el estado de una emergencia (taller)",
)
async def actualizar_estado(
    emergencia_id: int,
    data: ActualizarEstadoRequest,
    current=Depends(require_role("tecnico", "admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    """
    CU15: Gestión de Solicitud Taller —
    El técnico actualiza el estado del servicio (INICIADA, ATENDIDO, CANCELADO).
    El taller del técnico se extrae del JWT para validación multi-inquilino.
    """
    taller_cod = current.get("taller")
    historial = await emergencia_service.actualizar_estado_emergencia(
        emergencia_id, data, taller_cod, db
    )
    return {"message": "Estado actualizado correctamente", "historial_id": historial.id}

@router.post(
    "/solicitudes/{emergencia_id}/finalizar",
    summary="CU15 — Finalizar emergencia y solicitar pago",
)
async def finalizar_emergencia(
    emergencia_id: int,
    data: dict, # O usar FinalizarEmergenciaRequest si prefieres tipado fuerte
    current=Depends(require_role("tecnico", "admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    """
    CU15: Gestión de Solicitud Taller —
    Finaliza el servicio, genera el registro de pago y notifica al cliente 
    el monto final acordado.
    """
    taller_cod = current.get("taller")
    print(f"DEBUG FINALIZAR: user_id={current.get('user_id')}, role={current.get('role')}, taller={taller_cod}")
    return await emergencia_service.finalizar_emergencia(emergencia_id, data, taller_cod, db)

@router.post(
    "/solicitudes/{emergencia_id}/rechazar",
    summary="CU15 — Taller rechaza la emergencia asignada",
)
async def rechazar_emergencia(
    emergencia_id: int,
    current=Depends(require_role("tecnico", "admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    """
    CU15: El taller rechaza una emergencia después de que se le fue asignada 
    (o la cotización fue aceptada). La emergencia vuelve a buscar taller 
    y la cotización se cancela.
    """
    taller_cod = current.get("taller")
    return await emergencia_service.rechazar_emergencia_taller(emergencia_id, taller_cod, db)
