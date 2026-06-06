from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel
class Vehiculo(GenericModel):
    __tablename__ = "vehiculo"
    __table_args__ = {"schema": "public"}

    placa = Column(String(20), primary_key=True, index=True)
    marca = Column(String(100), nullable=False)
    modelo = Column(String(100), nullable=False)
    anio = Column("año", Integer, nullable=False)
    idCliente = Column(Integer, ForeignKey("public.cliente.id"), nullable=False, index=True)

    # Relaciones
    cliente = relationship("Cliente", back_populates="vehiculos")
    emergencias = relationship("Emergencia", back_populates="vehiculo")

    @classmethod
    async def get_by_placa(cls, db: AsyncSession, placa: str) -> Optional["Vehiculo"]:
        result = await db.execute(select(cls).where(cls.placa == placa))
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_cliente_id(cls, db: AsyncSession, cliente_id: int) -> list["Vehiculo"]:
        result = await db.execute(select(cls).where(cls.idCliente == cliente_id))
        return list(result.scalars().all())

