from sqlalchemy.ext.asyncio import AsyncSession

from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.catalogos import (
    EspecialidadCreate, EstadoCreate, PrioridadCreate, CategoriaProblemaCreate
)


# Especialidad
async def crear_especialidad(data: EspecialidadCreate, db: AsyncSession):
    obj = await Especialidad.create(db, obj_in=data.model_dump())
    await db.commit()
    return obj

async def listar_especialidades(db: AsyncSession):
    return await Especialidad.get_all(db, )

# Estado
async def crear_estado(data: EstadoCreate, db: AsyncSession):
    obj = await Especialidad.create(db, obj_in=data.model_dump())
    await db.commit()
    return obj

async def listar_estados(db: AsyncSession):
    return await Especialidad.get_all(db, )

# Prioridad
async def listar_prioridades(db: AsyncSession):
    return await Especialidad.get_all(db, )

# Categoria
async def listar_categorias(db: AsyncSession):
    return await Especialidad.get_all(db, )
