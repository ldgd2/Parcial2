from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Tecnico(Base):
    __tablename__ = "tecnico"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    correo = Column(String(255), nullable=False, unique=True, index=True)
    contrasena = Column("contraseña", String(255), nullable=False)
    telefono = Column(String(20), nullable=False)
    estado = Column(String(20), nullable=False, server_default="ACTIVO", default="ACTIVO")
    idTaller = Column(String(10), ForeignKey("taller.cod"), nullable=False, index=True)

    # Relaciones
    taller = relationship("Taller", back_populates="tecnicos")
    especialidades = relationship("Especialidad", secondary="tecnico_especialidad", back_populates="tecnicos")
    emergencias_asignadas = relationship("Emergencia", secondary="asignacion_tecnico_emergencia", back_populates="tecnicos_asignados")
