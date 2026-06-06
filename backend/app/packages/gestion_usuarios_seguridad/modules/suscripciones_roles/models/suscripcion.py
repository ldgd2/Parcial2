from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel

class PlanSuscripcion(GenericModel):
    __tablename__ = "plan_suscripcion"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True) # Gratuita, Standar, Profesional, Deluxe
    descripcion = Column(String(500), nullable=True)
    precio_mensual = Column(Float, default=0.0)
    
    # Límites
    max_sucursales = Column(Integer, default=1)
    max_tecnicos = Column(Integer, default=5)
    max_admins_sucursal = Column(Integer, default=1)
    
    # Relaciones
    talleres = relationship("Taller", back_populates="plan")
    permisos = relationship("Permiso", secondary="public.plan_permiso", back_populates="planes")
