from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.generic_model import GenericModel

class Calificacion(GenericModel):
    __tablename__ = "calificacion"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    idEmergencia = Column(Integer, ForeignKey("public.emergencia.id"), unique=True, nullable=False)
    idCliente = Column(Integer, ForeignKey("public.usuario.id"), nullable=False)
    idTaller = Column(String(10), ForeignKey("public.taller.cod"), nullable=False)
    idTecnico = Column(Integer, ForeignKey("public.tecnico.id"), nullable=False)
    
    puntuacion_taller = Column(Integer, nullable=False)
    puntuacion_tecnico = Column(Integer, nullable=False)
    comentario = Column(String(500), nullable=True)
    estado = Column(String(20), nullable=False, default="PUBLICADA")  # PUBLICADA, OCULTADA
    fecha = Column(DateTime, default=datetime.utcnow)

    emergencia = relationship("Emergencia", back_populates="calificacion")
    cliente = relationship("Usuario", foreign_keys=[idCliente])
    taller = relationship("Taller")
    tecnico = relationship("Tecnico")
