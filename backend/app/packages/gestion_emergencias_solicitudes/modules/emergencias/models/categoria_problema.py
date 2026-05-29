from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class CategoriaProblema(Base):
    __tablename__ = "categoria_problema"

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(255), nullable=False)
    idEspecialidad = Column(Integer, ForeignKey("especialidad.id"), nullable=True)

    especialidad = relationship("Especialidad")
