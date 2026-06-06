from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel
class AsignacionEspecialidad(GenericModel):
    __tablename__ = "asignacion_especialidad"
    __table_args__ = {"schema": "public"}

    idTaller = Column(String(10), ForeignKey("public.taller.cod"), primary_key=True)
    idEspecialidad = Column(Integer, ForeignKey("public.especialidad.id"), primary_key=True)

    # Relaciones
    taller = relationship("Taller", back_populates="asignaciones")
    especialidad = relationship("Especialidad")
