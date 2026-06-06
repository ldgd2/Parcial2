from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.db.generic_model import GenericModel
class FCMToken(GenericModel):
    __tablename__ = "fcm_token"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    idUsuario = Column(Integer, ForeignKey("public.usuario.id"), nullable=True, index=True)
    idCliente = Column(Integer, ForeignKey("public.cliente.id"), nullable=True, index=True)
    token = Column(String(512), nullable=False, unique=True)
    dispositivo = Column(String(50), nullable=True) # ej: android, ios, web
    fecha_registro = Column(DateTime, default=datetime.datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", backref="fcm_tokens")
    cliente = relationship("Cliente", backref="fcm_tokens")

    @classmethod
    async def delete_by_token(cls, db: AsyncSession, token: str) -> None:
        await db.execute(delete(self.model).where(self.model.token == token))
        
    @classmethod
    async def get_by_user_or_client(cls, db: AsyncSession, user_id: int) -> list["FCMToken"]:
        stmt = select(self.model).where(
            or_(
                self.model.idUsuario == user_id, 
                self.model.idCliente == user_id
            )
        )
        result = await db.execute(stmt)
        return result.scalars().all()

