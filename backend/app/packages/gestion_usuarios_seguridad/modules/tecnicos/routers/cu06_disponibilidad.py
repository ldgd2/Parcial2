"""
CU06 — Gestión de Disponibilidad del Taller

PATCH /talleres/{cod}/disponibilidad → Actualizar disponibilidad operativa
GET   /talleres/mis-talleres         → Listar talleres del admin autenticado
GET   /talleres/{cod}                → Detalle de un taller por código
POST  /talleres/                     → Crear taller
PUT   /talleres/{cod}                → Actualizar información del taller
PATCH /talleres/{cod}/desactivar     → Desactivar taller
GET   /talleres/activos              → Listar talleres activos (público)
POST  /talleres/{cod}/especialidades → Asignar especialidades al taller
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.dependencies import require_role
from app.packages.gestion_usuarios_seguridad.modules.tenants.schemas.taller import TallerOut, DisponibilidadUpdate, TallerCreate, TallerUpdate
from app.packages.gestion_usuarios_seguridad.modules.tenants.services import taller_service

router = APIRouter(prefix="/talleres", tags=["GPS — Talleres / Disponibilidad (CU06)"])


@router.get(
    "/mis-talleres",
    response_model=list[TallerOut],
    summary="Listar talleres del administrador logueado",
)
async def mis_talleres(
    current=Depends(require_role("admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    return await taller_service.listar_talleres_admin(current["user_id"], db)


@router.get(
    "/activos",
    response_model=list[TallerOut],
    summary="Listar talleres activos (público)",
)
async def talleres_activos(db: AsyncSession = Depends(get_db)):
    return await taller_service.listar_talleres_activos(db)


@router.get(
    "/{cod}",
    response_model=TallerOut,
    summary="Obtener detalle de un taller por código",
)
async def obtener_taller(
    cod: str,
    current=Depends(require_role("admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    taller = await taller_service.obtener_taller_por_codigo(cod, db)
    if not taller:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Taller no encontrado")

    # Si es admin de sucursal, sobrescribir latitud/longitud con los de su sucursal
    # para que el radar frontend se centre en la sucursal y no en la matriz.
    if current.get("role") == "admin_sucursal" and current.get("sucursal"):
        from app.packages.gestion_usuarios_seguridad.modules.tenants.models.sucursal import Sucursal
        sucursal = await db.get(Sucursal, current["sucursal"])
        if sucursal and sucursal.latitud and sucursal.longitud:
            # TallerOut is a pydantic model, but here taller is a SQLAlchemy model.
            # We can't modify the SQLAlchemy object in-place cleanly without affecting the session.
            # But FastAPI automatically serializes it. We can convert to dict, update, and return the dict.
            taller_dict = taller.__dict__.copy()
            taller_dict["latitud"] = sucursal.latitud
            taller_dict["longitud"] = sucursal.longitud
            return taller_dict

    return taller


@router.post(
    "/",
    response_model=TallerOut,
    summary="Crear un nuevo taller (Admin)",
)
async def crear_taller(
    data: TallerCreate,
    current=Depends(require_role("admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    return await taller_service.crear_taller(data, current["user_id"], db)


@router.put(
    "/{cod}",
    response_model=TallerOut,
    summary="Actualizar información del taller",
)
async def actualizar_taller(
    cod: str,
    data: TallerUpdate,
    current=Depends(require_role("admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    return await taller_service.actualizar_taller(cod, data, db)


@router.patch(
    "/{cod}/desactivar",
    response_model=TallerOut,
    summary="Desactivar un taller",
)
async def desactivar_taller(
    cod: str,
    current=Depends(require_role("admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    return await taller_service.actualizar_taller(cod, TallerUpdate(estado="INACTIVO"), db)


@router.post(
    "/{cod}/especialidades",
    summary="Asignar especialidades a un taller",
)
async def asignar_especialidades(
    cod: str,
    especialidades_ids: list[int],
    current=Depends(require_role("admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db),
):
    return await taller_service.actualizar_especialidades_taller(cod, especialidades_ids, db)


@router.patch(
    "/{cod}/disponibilidad",
    response_model=TallerOut,
    summary="CU06 — Gestión de disponibilidad del taller",
)
async def actualizar_disponibilidad(
    cod: str,
    data: DisponibilidadUpdate,
    current=Depends(require_role("tecnico")),
    db: AsyncSession = Depends(get_db),
):
    """Solo técnicos autenticados del taller pueden cambiar su estado operativo."""
    return await taller_service.actualizar_disponibilidad(cod, data, db)
