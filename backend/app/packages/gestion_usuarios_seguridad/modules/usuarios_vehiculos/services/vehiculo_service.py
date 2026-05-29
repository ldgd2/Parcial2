from sqlalchemy.ext.asyncio import AsyncSession
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.schemas.vehiculo import VehiculoCreate, VehiculoUpdate
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.repositories.vehiculo_repo import VehiculoRepository

async def crear_vehiculo(data: VehiculoCreate, db: AsyncSession):
    repo = VehiculoRepository(db)
    # The repository handles the flush/commit within the service transaction scope
    # Wait, the old service did `db.commit()`. BaseRepository does `db.flush()`.
    # Services are usually responsible for calling `db.commit()` in their caller routers, 
    # but since the old code did it, I'll let the caller router handle it or I can just call db.commit() here if necessary.
    vehiculo = await repo.create(obj_in=data.model_dump())
    await db.commit() # Keeping commit for backward compatibility if the router doesn't do it
    return vehiculo

async def obtener_vehiculo(placa: str, db: AsyncSession):
    repo = VehiculoRepository(db)
    return await repo.get_by_placa(placa)

async def actualizar_vehiculo(placa: str, data: VehiculoUpdate, db: AsyncSession):
    repo = VehiculoRepository(db)
    vehiculo = await repo.get_by_placa(placa)
    if not vehiculo:
        return None
    vehiculo = await repo.update(db_obj=vehiculo, obj_in=data)
    await db.commit() # Keeping commit for backward compatibility
    return vehiculo
