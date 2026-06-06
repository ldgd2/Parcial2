from sqlalchemy.ext.asyncio import AsyncSession
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.schemas.vehiculo import VehiculoCreate, VehiculoUpdate

async def crear_vehiculo(data: VehiculoCreate, db: AsyncSession):
    # The repository handles the flush/commit within the service transaction scope
    # Wait, the old service did `db.commit()`. BaseRepository does `db.flush()`.
    # Services are usually responsible for calling `db.commit()` in their caller routers, 
    # but since the old code did it, I'll let the caller router handle it or I can just call db.commit() here if necessary.
    vehiculo = await Vehiculo.create(db, obj_in=data.model_dump())
    await db.commit() # Keeping commit for backward compatibility if the router doesn't do it
    return vehiculo

async def obtener_vehiculo(placa: str, db: AsyncSession):
    return await Vehiculo.get_by_placa(db, placa)

async def actualizar_vehiculo(placa: str, data: VehiculoUpdate, db: AsyncSession):
    vehiculo = await Vehiculo.get_by_placa(db, placa)
    if not vehiculo:
        return None
    vehiculo = await vehiculo.update(db, obj_in=data)
    await db.commit() # Keeping commit for backward compatibility
    return vehiculo
