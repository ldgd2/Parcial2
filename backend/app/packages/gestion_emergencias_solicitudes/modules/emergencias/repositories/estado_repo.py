from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.db.repository import BaseRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado

class EstadoCreate(BaseModel):
    nombre: str

class EstadoUpdate(BaseModel):
    pass

class EstadoRepository(BaseRepository[Estado, EstadoCreate, EstadoUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Estado, db)

    async def get_by_nombre(self, nombre: str) -> Optional[Estado]:
        result = await self.db.execute(select(Estado).where(Estado.nombre == nombre))
        return result.scalar_one_or_none()
