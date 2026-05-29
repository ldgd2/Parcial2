from sqlalchemy.ext.asyncio import AsyncSession

from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.catalogos import (
    EspecialidadCreate, EstadoCreate, PrioridadCreate, CategoriaProblemaCreate
)

from app.packages.gestion_usuarios_seguridad.modules.tecnicos.repositories.especialidad_repo import EspecialidadRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.estado_repo import EstadoRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.prioridad_repo import PrioridadRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.categoria_repo import CategoriaProblemaRepository

# Especialidad
async def crear_especialidad(data: EspecialidadCreate, db: AsyncSession):
    repo = EspecialidadRepository(db)
    obj = await repo.create(obj_in=data.model_dump())
    await db.commit()
    return obj

async def listar_especialidades(db: AsyncSession):
    repo = EspecialidadRepository(db)
    return await repo.get_all()

# Estado
async def crear_estado(data: EstadoCreate, db: AsyncSession):
    repo = EstadoRepository(db)
    obj = await repo.create(obj_in=data.model_dump())
    await db.commit()
    return obj

async def listar_estados(db: AsyncSession):
    repo = EstadoRepository(db)
    return await repo.get_all()

# Prioridad
async def listar_prioridades(db: AsyncSession):
    repo = PrioridadRepository(db)
    return await repo.get_all()

# Categoria
async def listar_categorias(db: AsyncSession):
    repo = CategoriaProblemaRepository(db)
    return await repo.get_all()
