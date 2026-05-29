from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class AsignacionEspecialidad(Base):
    __tablename__ = "asignacion_especialidad"

    idTaller = Column(String(10), ForeignKey("taller.cod"), primary_key=True)
    idEspecialidad = Column(Integer, ForeignKey("especialidad.id"), primary_key=True)

    # Relaciones
    taller = relationship("Taller", back_populates="asignaciones")
    especialidad = relationship("Especialidad")
