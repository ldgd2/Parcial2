from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, Integer, ForeignKey
from app.db.generic_model import GenericModel
class AsignacionTecnicoEmergencia(GenericModel):
    __tablename__ = "asignacion_tecnico_emergencia"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    idTecnico = Column(Integer, ForeignKey("public.tecnico.id"), nullable=False, index=True)
    idEmergencia = Column(Integer, ForeignKey("public.emergencia.id"), nullable=False, index=True)

    @classmethod
    async def delete_by_emergencia(cls, db: AsyncSession, emergencia_id: int):
        await db.execute(
            delete(cls).where(cls.idEmergencia == emergencia_id)
        )
        await db.flush()

