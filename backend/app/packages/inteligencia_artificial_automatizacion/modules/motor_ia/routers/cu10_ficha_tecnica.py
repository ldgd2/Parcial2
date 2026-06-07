"""
CU10 — Generación de Ficha Técnica (IA + Edición Manual del Taller)

PATCH /talleres/{emergencia_id}/ficha-tecnica → El taller completa/corrige la ficha

La ficha técnica es generada inicialmente por IA al reportar la emergencia (CU08/CU09).
El taller puede editarla post-servicio con los datos reales del diagnóstico.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import require_role
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.services import emergencia_service

router = APIRouter(prefix="/talleres", tags=["IA — Ficha Técnica (CU10)"])


@router.patch(
    "/{emergencia_id}/ficha-tecnica",
    summary="CU10 — El taller completa/corrige la ficha técnica real post-servicio",
)
async def actualizar_ficha_tecnica(
    emergencia_id: int,
    data: dict,
    current=Depends(require_role("admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    """
    CU10: Generación de Ficha Técnica —
    Permite al taller completar o corregir el diagnóstico, piezas y acciones
    realizadas, reemplazando/complementando lo generado por la IA con datos reales.
    """
    return await emergencia_service.actualizar_ficha_tecnica(
        emergencia_id, data, current.get("taller"), db
    )
