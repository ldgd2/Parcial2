from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel
class Evidencia(GenericModel):
    __tablename__ = "evidencia"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    direccion = Column(String(500), nullable=False)
    idEmergencia = Column(Integer, ForeignKey("public.emergencia.id"), nullable=False, index=True)

    emergencia = relationship("Emergencia", back_populates="evidencias")

    @classmethod
    async def delete_by_emergencia(cls, db: AsyncSession, id_emergencia: int):
        await db.execute(delete(cls).where(cls.idEmergencia == id_emergencia))
        await db.flush()

