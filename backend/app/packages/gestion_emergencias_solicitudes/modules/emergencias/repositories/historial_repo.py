from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db.repository import BaseRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.historial_estado import HistorialEstado

class HistorialEstadoCreate(BaseModel):
    idEmergencia: int
    idEstado: int

class HistorialEstadoUpdate(BaseModel):
    pass

class HistorialEstadoRepository(BaseRepository[HistorialEstado, HistorialEstadoCreate, HistorialEstadoUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(HistorialEstado, db)
