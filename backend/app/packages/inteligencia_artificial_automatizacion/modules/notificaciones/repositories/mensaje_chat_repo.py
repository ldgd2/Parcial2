from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from app.db.repository import BaseRepository
from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.models.mensaje_chat import MensajeChat

class MensajeChatCreate(BaseModel):
    idEmergencia: int
    remitente_id: int
    rol_remitente: str
    contenido: str | None = None
    imagen_url: str | None = None
    audio_url: str | None = None

class MensajeChatUpdate(BaseModel):
    pass

class MensajeChatRepository(BaseRepository[MensajeChat, MensajeChatCreate, MensajeChatUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(MensajeChat, db)
        
    async def get_historial_por_emergencia(self, emergencia_id: int) -> list[MensajeChat]:
        stmt = (
            select(self.model)
            .where(self.model.idEmergencia == emergencia_id)
            .order_by(self.model.fecha_envio.asc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
