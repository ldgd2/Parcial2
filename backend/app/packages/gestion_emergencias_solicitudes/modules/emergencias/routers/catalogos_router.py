"""
Catálogos — Transversal a todos los paquetes
GET  /catalogos/especialidades → Listar especialidades disponibles
POST /catalogos/especialidades → Crear nueva especialidad (solo admin)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select

from app.db.session import get_db
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.especialidad import Especialidad
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.catalogos import EspecialidadOut, EspecialidadCreate
from app.core.dependencies import require_role

router = APIRouter(prefix="/catalogos", tags=["Catálogos"])


@router.get("/especialidades", response_model=list[EspecialidadOut])
async def listar_especialidades(db: AsyncSession = Depends(get_db)):
    """Lista todas las especialidades disponibles en el sistema."""
    result = await db.execute(select(Especialidad).order_by(Especialidad.nombre))
    return result.scalars().all()


@router.post("/especialidades", response_model=EspecialidadOut)
async def crear_especialidad(
    data: EspecialidadCreate,
    current=Depends(require_role("admin", "admin_sucursal")),
    db: AsyncSession = Depends(get_db)
):
    """Crea una nueva especialidad en el catálogo global."""
    existing = await db.execute(select(Especialidad).where(Especialidad.nombre == data.nombre))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La especialidad ya existe."
        )
    nueva = Especialidad(**data.model_dump())
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva

from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado

@router.get("/estados")
async def listar_estados(db: AsyncSession = Depends(get_db)):
    """Lista todos los estados (DEBUG)"""
    result = await db.execute(select(Estado.id, Estado.nombre))
    return [{"id": r.id, "nombre": r.nombre} for r in result.fetchall()]

