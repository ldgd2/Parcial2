from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.session import Base


class Taller(Base):
    __tablename__ = "taller"

    cod = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    direccion = Column(String(500), nullable=False)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    calificacion_promedio = Column(Float, nullable=False, default=5.0, server_default="5.0")
    estado = Column(String(20), nullable=False, default="ACTIVO")
    id_admin = Column(Integer, ForeignKey("usuario.id", name="fk_taller_admin", use_alter=True), nullable=True) # El admin que lo creó

    # Relaciones
    tecnicos = relationship("Tecnico", back_populates="taller")
    usuarios = relationship("Usuario", back_populates="taller", foreign_keys="Usuario.idTaller")
    emergencias = relationship("Emergencia", back_populates="taller", foreign_keys="Emergencia.idTaller")
    asignaciones = relationship("AsignacionEspecialidad", back_populates="taller")
    
    admin = relationship("Usuario", foreign_keys=[id_admin])
