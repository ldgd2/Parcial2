from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from sqlalchemy.orm import selectinload

from app.db.repository import BaseRepository
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico_especialidad import TecnicoEspecialidad

class TecnicoCreate(BaseModel):
    nombre: str
    correo: str
    contrasena: str
    telefono: Optional[str] = None
    idTaller: Optional[str] = None
    estado: str = "ACTIVO"

class TecnicoUpdate(BaseModel):
    pass

class TecnicoRepository(BaseRepository[Tecnico, TecnicoCreate, TecnicoUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Tecnico, db)

    async def get_by_correo(self, correo: str) -> Optional[Tecnico]:
        result = await self.db.execute(select(Tecnico).where(Tecnico.correo == correo))
        return result.scalar_one_or_none()

    async def get_with_especialidades(self, id: int) -> Optional[Tecnico]:
        stmt = select(Tecnico).options(selectinload(Tecnico.especialidades)).where(Tecnico.id == id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_taller_with_especialidades(self, idTaller: str) -> list[Tecnico]:
        stmt = select(Tecnico).options(selectinload(Tecnico.especialidades)).where(Tecnico.idTaller == idTaller)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_especialidades(self, tecnico_id: int, especialidades_ids: list[int]):
        # 1. Eliminar asignaciones actuales
        await self.db.execute(
            delete(TecnicoEspecialidad).where(TecnicoEspecialidad.idTecnico == tecnico_id)
        )
        # 2. Insertar nuevas
        for esp_id in especialidades_ids:
            self.db.add(TecnicoEspecialidad(idTecnico=tecnico_id, idEspecialidad=esp_id))
        await self.db.flush()
