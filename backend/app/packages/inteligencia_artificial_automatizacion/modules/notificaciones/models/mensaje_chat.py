from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel
import datetime

class MensajeChat(GenericModel):
    __tablename__ = "mensajes_chat"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    idEmergencia = Column(Integer, ForeignKey("public.emergencia.id"), nullable=False)
    remitente_id = Column(Integer, nullable=False) # ID de Cliente o Usuario
    rol_remitente = Column(String(20), nullable=False) # "cliente", "tecnico", "admin"
    contenido = Column(Text, nullable=True)
    imagen_url = Column(String(255), nullable=True)
    audio_url = Column(String(255), nullable=True)
    fecha_envio = Column(DateTime, default=datetime.datetime.now)

    # Relaciones
    emergencia = relationship("Emergencia", back_populates="mensajes_chat")

    @classmethod
    async def get_historial_por_emergencia(cls, db: AsyncSession, emergencia_id: int) -> list["MensajeChat"]:
        stmt = (
            select(self.model)
            .where(self.model.idEmergencia == emergencia_id)
            .order_by(self.model.fecha_envio.asc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

