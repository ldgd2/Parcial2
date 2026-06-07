from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel

class SucursalEspecialidad(GenericModel):
    __tablename__ = "sucursal_especialidad"
    __table_args__ = {"schema": "public"}

    id_sucursal = Column(Integer, ForeignKey("public.sucursal.id"), primary_key=True)
    id_especialidad = Column(Integer, ForeignKey("public.especialidad.id"), primary_key=True)

    # Relaciones
    sucursal = relationship("Sucursal", back_populates="especialidades")
    especialidad = relationship("Especialidad")
