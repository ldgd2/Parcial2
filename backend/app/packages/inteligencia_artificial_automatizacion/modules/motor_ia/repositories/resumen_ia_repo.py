from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.db.repository import BaseRepository
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.models.resumen_ia import ResumenIA

class ResumenIACreate(BaseModel):
    resumen: str
    ficha_tecnica: Optional[dict] = None
    recomendaciones_taller: Optional[str] = None
    motivo_rechazo: Optional[str] = None
    idEmergencia: int

class ResumenIAUpdate(BaseModel):
    pass

class ResumenIARepository(BaseRepository[ResumenIA, ResumenIACreate, ResumenIAUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(ResumenIA, db)

    async def get_by_emergencia(self, idEmergencia: int) -> Optional[ResumenIA]:
        result = await self.db.execute(select(ResumenIA).where(ResumenIA.idEmergencia == idEmergencia))
        return result.scalar_one_or_none()
