from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel
class Usuario(GenericModel):
    __tablename__ = "usuario"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    apellido = Column(String(255), nullable=False)
    correo = Column(String(255), nullable=False, unique=True, index=True)
    contrasena = Column("contraseña", String(255), nullable=False)
    estado = Column(String(20), nullable=False, server_default="ACTIVO", default="ACTIVO")
    fcm_token = Column(String(512), nullable=True)
    idTaller = Column(String(10), ForeignKey("public.taller.cod"), nullable=True, index=True)
    idSucursal = Column(Integer, ForeignKey("public.sucursal.id"), nullable=True, index=True)
    id_rol = Column(Integer, ForeignKey("public.rol.id"), nullable=True)

    # Relaciones
    taller = relationship("Taller", back_populates="usuarios", foreign_keys=[idTaller])
    sucursal = relationship("Sucursal")
    rol = relationship("Rol")

    @classmethod
    async def get_by_correo(cls, db: AsyncSession, correo: str) -> Optional["Usuario"]:
        result = await db.execute(select(cls).where(cls.correo == correo))
        return result.scalar_one_or_none()

