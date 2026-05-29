from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

class Especialidad(Base):
    __tablename__ = "especialidad"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=False)

    # Relación inversa
    tecnicos = relationship("Tecnico", secondary="tecnico_especialidad", back_populates="especialidades")
