from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel
class CategoriaProblema(GenericModel):
    __tablename__ = "categoria_problema"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(255), nullable=False)
    idEspecialidad = Column(Integer, ForeignKey("public.especialidad.id"), nullable=True)

    especialidad = relationship("Especialidad")

    @classmethod
    async def get_by_especialidades(cls, db: AsyncSession, especialidades_ids: list[int]) -> list["CategoriaProblema"]:
        result = await db.execute(
            select(cls).where(cls.idEspecialidad.in_(especialidades_ids))
        )
        return list(result.scalars().all())

