from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from sqlalchemy.orm import joinedload

from app.db.repository import BaseRepository
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_emergencias_solicitudes.modules.auxilio_solicitudes.models.asignacion_especialidad import AsignacionEspecialidad

class TallerCreate(BaseModel):
    cod: str
    nombre: str
    direccion: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    estado: str
    id_admin: Optional[int] = None

class TallerUpdate(BaseModel):
    pass

class TallerRepository(BaseRepository[Taller, TallerCreate, TallerUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Taller, db)

    async def get_by_cod(self, cod: str) -> Optional[Taller]:
        result = await self.db.execute(select(Taller).where(Taller.cod == cod))
        return result.scalar_one_or_none()

    async def get_with_especialidades(self, cod: str) -> Optional[Taller]:
        stmt = (
            select(Taller)
            .options(joinedload(Taller.asignaciones).joinedload(AsignacionEspecialidad.especialidad))
            .where(Taller.cod == cod)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def update_especialidades(self, cod: str, especialidades_ids: list[int]):
        await self.db.execute(
            delete(AsignacionEspecialidad).where(AsignacionEspecialidad.idTaller == cod)
        )
        for e_id in especialidades_ids:
            self.db.add(AsignacionEspecialidad(idTaller=cod, idEspecialidad=e_id))
        await self.db.flush()

    async def get_by_admin_with_especialidades(self, admin_id: int) -> list[Taller]:
        stmt = (
            select(Taller)
            .options(joinedload(Taller.asignaciones).joinedload(AsignacionEspecialidad.especialidad))
            .where(Taller.id_admin == admin_id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_activos(self) -> list[Taller]:
        result = await self.db.execute(select(Taller).where(Taller.estado == "ACTIVO"))
        return list(result.scalars().all())
