"""
CU07 — Gestionar Técnico
CU13 — Gestionar Rol (Especialidades)

POST   /tecnicos/                        → CU07 Registrar técnico
PUT    /tecnicos/{id}                    → CU07 Actualizar técnico
DELETE /tecnicos/{id}                    → CU07 Desactivar técnico
GET    /tecnicos/taller/{idTaller}       → CU07 Listar técnicos de un taller
GET    /tecnicos/perfil                  → CU07 Perfil del técnico autenticado
PUT    /tecnicos/{id}/especialidades     → CU13 Gestionar rol / asignar especialidades
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.dependencies import require_role
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.schemas.tecnico import TecnicoOut, TecnicoCreate, TecnicoUpdate
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.services import tecnico_service

router = APIRouter(prefix="/tecnicos", tags=["GPS — Técnicos (CU07/CU13)"])


# ─── CU07: Gestionar Técnico ─────────────────────────────────────────────────

@router.post(
    "/",
    response_model=TecnicoOut,
    status_code=201,
    summary="CU07 — Registrar un nuevo técnico",
)
async def crear_tecnico(
    data: TecnicoCreate,
    current=Depends(require_role("admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    """Solo admins del taller pueden registrar técnicos."""
    if not data.idSucursal:
        data.idSucursal = current.get("sucursal")
    return await tecnico_service.crear_tecnico(data, db)


@router.get(
    "/taller/{idTaller}",
    response_model=list[TecnicoOut],
    summary="CU07 — Listar técnicos de un taller",
)
async def listar_tecnicos_taller(
    idTaller: str,
    current=Depends(require_role("admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    return await tecnico_service.obtener_tecnicos_taller(idTaller, db)


@router.get(
    "/perfil",
    response_model=TecnicoOut,
    summary="CU07 — Perfil del técnico autenticado",
)
async def perfil(
    current=Depends(require_role("tecnico")),
    db: AsyncSession = Depends(get_db),
):
    tecnico = await tecnico_service.obtener_tecnico_by_id(current["user_id"], db)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    return tecnico


@router.put(
    "/{tecnico_id}",
    response_model=TecnicoOut,
    summary="CU07 — Actualizar perfil de un técnico",
)
async def actualizar_tecnico(
    tecnico_id: int,
    data: TecnicoUpdate,
    current=Depends(require_role("admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    return await tecnico_service.actualizar_tecnico(tecnico_id, data, db)


@router.delete(
    "/{tecnico_id}",
    summary="CU07 — Desactivar un técnico",
)
async def desactivar_tecnico(
    tecnico_id: int,
    current=Depends(require_role("admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    await tecnico_service.desactivar_tecnico(tecnico_id, db)
    return {"status": "ok", "message": "Técnico desactivado"}


# ─── CU13: Gestionar Rol ─────────────────────────────────────────────────────

@router.put(
    "/{tecnico_id}/especialidades",
    response_model=TecnicoOut,
    summary="CU13 — Gestionar Rol: asignar especialidades al técnico",
)
async def asignar_especialidades_tecnico(
    tecnico_id: int,
    especialidades_ids: list[int],
    current=Depends(require_role("admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    """
    CU13: Reemplaza las especialidades del técnico con la nueva selección.
    Esto define su 'rol' operativo dentro del taller (ej: Eléctrico, Mecánico).
    """
    return await tecnico_service.actualizar_especialidades_tecnico(tecnico_id, especialidades_ids, db)
