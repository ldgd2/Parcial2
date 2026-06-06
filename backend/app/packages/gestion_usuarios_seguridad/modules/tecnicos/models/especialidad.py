from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel
class Especialidad(GenericModel):
    __tablename__ = "especialidad"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=False)

    # Relación inversa
    tecnicos = relationship("Tecnico", secondary="public.tecnico_especialidad", back_populates="especialidades")
