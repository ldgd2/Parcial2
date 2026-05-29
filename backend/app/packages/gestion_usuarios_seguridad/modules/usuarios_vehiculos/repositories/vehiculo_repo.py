from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db.repository import BaseRepository
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.vehiculo import Vehiculo
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.schemas.vehiculo import VehiculoCreate

class VehiculoUpdate(BaseModel):
    pass

class VehiculoRepository(BaseRepository[Vehiculo, VehiculoCreate, VehiculoUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Vehiculo, db)

    async def get_by_placa(self, placa: str) -> Optional[Vehiculo]:
        result = await self.db.execute(select(Vehiculo).where(Vehiculo.placa == placa))
        return result.scalar_one_or_none()

    async def get_by_cliente_id(self, cliente_id: int) -> list[Vehiculo]:
        result = await self.db.execute(select(Vehiculo).where(Vehiculo.idCliente == cliente_id))
        return list(result.scalars().all())
