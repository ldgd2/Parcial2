from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db.repository import BaseRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.prioridad import Prioridad

class PrioridadCreate(BaseModel):
    descripcion: str

class PrioridadUpdate(BaseModel):
    pass

class PrioridadRepository(BaseRepository[Prioridad, PrioridadCreate, PrioridadUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Prioridad, db)
