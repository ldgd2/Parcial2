from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, delete
from typing import List
from pydantic import BaseModel
from app.db.repository import BaseRepository
from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.models.fcm_token import FCMToken

class FCMTokenCreate(BaseModel):
    token: str
    dispositivo: str = "android"
    idCliente: int | None = None
    idUsuario: int | None = None

class FCMTokenUpdate(BaseModel):
    pass

class FCMTokenRepository(BaseRepository[FCMToken, FCMTokenCreate, FCMTokenUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(FCMToken, db)

    async def delete_by_token(self, token: str) -> None:
        await self.db.execute(delete(self.model).where(self.model.token == token))
        
    async def get_by_user_or_client(self, user_id: int) -> list[FCMToken]:
        stmt = select(self.model).where(
            or_(
                self.model.idUsuario == user_id, 
                self.model.idCliente == user_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
