from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db.repository import BaseRepository
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.cliente import Cliente
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.schemas.cliente import ClienteSimpleCreate

class ClienteUpdate(BaseModel):
    pass

class ClienteRepository(BaseRepository[Cliente, ClienteSimpleCreate, ClienteUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Cliente, db)

    async def get_by_correo(self, correo: str) -> Optional[Cliente]:
        result = await self.db.execute(select(Cliente).where(Cliente.correo == correo))
        return result.scalar_one_or_none()
