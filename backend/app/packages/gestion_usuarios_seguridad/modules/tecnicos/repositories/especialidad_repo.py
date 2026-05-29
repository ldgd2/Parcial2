from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db.repository import BaseRepository
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.especialidad import Especialidad

class EspecialidadCreate(BaseModel):
    nombre: str

class EspecialidadUpdate(BaseModel):
    pass

class EspecialidadRepository(BaseRepository[Especialidad, EspecialidadCreate, EspecialidadUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Especialidad, db)
