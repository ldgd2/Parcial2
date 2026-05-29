from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from pydantic import BaseModel
from typing import List
from app.db.repository import BaseRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.evidencia import Evidencia

class EvidenciaCreate(BaseModel):
    direccion: str
    idEmergencia: int

class EvidenciaUpdate(BaseModel):
    pass

class EvidenciaRepository(BaseRepository[Evidencia, EvidenciaCreate, EvidenciaUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Evidencia, db)

    async def delete_by_emergencia(self, id_emergencia: int):
        await self.db.execute(delete(Evidencia).where(Evidencia.idEmergencia == id_emergencia))
        await self.db.flush()
