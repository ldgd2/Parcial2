from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, Integer, String
from app.db.generic_model import GenericModel
class Estado(GenericModel):
    __tablename__ = "estado"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True, index=True)
    descripcion = Column(String(255), nullable=False)

    @classmethod
    async def get_by_nombre(cls, db: AsyncSession, nombre: str) -> Optional["Estado"]:
        result = await db.execute(select(cls).where(cls.nombre == nombre))
        return result.scalar_one_or_none()

