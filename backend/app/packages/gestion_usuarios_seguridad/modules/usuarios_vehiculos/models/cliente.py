from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel
class Cliente(GenericModel):
    __tablename__ = "cliente"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    correo = Column(String(255), nullable=False, unique=True, index=True)
    contrasena = Column("contraseña", String(255), nullable=False)
    estado = Column(String(20), nullable=False, server_default="ACTIVO", default="ACTIVO")
    fcm_token = Column(String(512), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)

    # Relaciones
    vehiculos = relationship("Vehiculo", back_populates="cliente")
    emergencias = relationship("Emergencia", back_populates="cliente")

    @classmethod
    async def get_by_correo(cls, db: AsyncSession, correo: str) -> Optional["Cliente"]:
        result = await db.execute(select(cls).where(cls.correo == correo))
        return result.scalar_one_or_none()

