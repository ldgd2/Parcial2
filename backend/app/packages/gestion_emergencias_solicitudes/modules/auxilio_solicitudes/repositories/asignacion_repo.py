from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from pydantic import BaseModel
from typing import List
from app.db.repository import BaseRepository
from app.packages.gestion_emergencias_solicitudes.modules.auxilio_solicitudes.models.asignacion_tecnico_emergencia import AsignacionTecnicoEmergencia

class AsignacionTecnicoEmergenciaCreate(BaseModel):
    idEmergencia: int
    idTecnico: int

class AsignacionTecnicoEmergenciaUpdate(BaseModel):
    pass

class AsignacionTecnicoEmergenciaRepository(BaseRepository[AsignacionTecnicoEmergencia, AsignacionTecnicoEmergenciaCreate, AsignacionTecnicoEmergenciaUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(AsignacionTecnicoEmergencia, db)

    async def delete_by_emergencia(self, emergencia_id: int):
        await self.db.execute(
            delete(AsignacionTecnicoEmergencia).where(AsignacionTecnicoEmergencia.idEmergencia == emergencia_id)
        )
        await self.db.flush()
