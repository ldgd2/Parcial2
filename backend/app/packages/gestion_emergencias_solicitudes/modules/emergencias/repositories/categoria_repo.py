from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List
from app.db.repository import BaseRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.categoria_problema import CategoriaProblema

class CategoriaProblemaCreate(BaseModel):
    descripcion: str
    idEspecialidad: int

class CategoriaProblemaUpdate(BaseModel):
    pass

class CategoriaProblemaRepository(BaseRepository[CategoriaProblema, CategoriaProblemaCreate, CategoriaProblemaUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(CategoriaProblema, db)

    async def get_by_especialidades(self, especialidades_ids: List[int]) -> List[CategoriaProblema]:
        result = await self.db.execute(
            select(CategoriaProblema).where(CategoriaProblema.idEspecialidad.in_(especialidades_ids))
        )
        return list(result.scalars().all())
