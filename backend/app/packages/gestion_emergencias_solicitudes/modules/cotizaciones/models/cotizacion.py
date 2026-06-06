from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel
class Cotizacion(GenericModel):
    __tablename__ = "cotizacion"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    idEmergencia = Column(Integer, ForeignKey("public.emergencia.id"), nullable=False, index=True)
    idTaller = Column(String(10), ForeignKey("public.taller.cod"), nullable=False, index=True)
    
    descripcion_servicio = Column(Text, nullable=False)
    costo_mano_obra = Column(Float, nullable=False)
    costo_repuestos = Column(Float, default=0.0)
    tiempo_estimado_horas = Column(Integer, nullable=False)
    condiciones = Column(Text, nullable=True)
    
    # Estados sugeridos: PENDIENTE, ACEPTADA, RECHAZADA, EN_REVISION
    estado = Column(String(20), nullable=False, default="PENDIENTE")
    
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_actualizacion = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relaciones
    emergencia = relationship("Emergencia", back_populates="cotizaciones")
    taller = relationship("Taller")
