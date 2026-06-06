from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel
class ResumenIA(GenericModel):
    __tablename__ = "resumen_ia"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    resumen = Column("Resumen", Text, nullable=False)
    ficha_tecnica = Column("FichaTecnica", JSON, nullable=True)
    recomendaciones_taller = Column(Text, nullable=True)
    motivo_rechazo = Column(Text, nullable=True)
    idEmergencia = Column(Integer, ForeignKey("public.emergencia.id"), nullable=False, index=True)

    emergencia = relationship("Emergencia", back_populates="resumen_ia")

    @classmethod
    async def get_by_emergencia(cls, db: AsyncSession, idEmergencia: int) -> Optional["ResumenIA"]:
        result = await db.execute(select(cls).where(cls.idEmergencia == idEmergencia))
        return result.scalar_one_or_none()

