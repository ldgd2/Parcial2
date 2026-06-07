from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel
class Cotizacion(GenericModel):
    __tablename__ = "cotizacion"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    idEmergencia = Column(Integer, ForeignKey("public.emergencia.id"), nullable=False, index=True)
    idTaller = Column(String(10), ForeignKey("public.taller.cod"), nullable=False, index=True)
    
    descripcion_servicio = Column(Text, nullable=True) # Optional summary
    moneda = Column(String(3), nullable=False, default="BOB") # BOB or USD
    lista_productos = Column(JSON, nullable=False, default=[]) # e.g. [{"nombre": "Filtro", "precio": 50, "cantidad": 1}]
    lista_servicios = Column(JSON, nullable=False, default=[]) # e.g. [{"nombre": "Mano de obra", "precio": 100}]
    subtotal_productos = Column(Float, nullable=False, default=0.0)
    subtotal_servicios = Column(Float, nullable=False, default=0.0)
    total_general = Column(Float, nullable=False, default=0.0)
    tiempo_estimado = Column(String(50), nullable=False)
    condiciones = Column(Text, nullable=True)
    
    # Estados sugeridos: PENDIENTE, ACEPTADA, RECHAZADA, EN_REVISION
    estado = Column(String(20), nullable=False, default="PENDIENTE")
    
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_actualizacion = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relaciones
    emergencia = relationship("Emergencia", back_populates="cotizaciones")
    taller = relationship("Taller")
