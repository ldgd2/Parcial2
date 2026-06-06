from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel

class Sucursal(GenericModel):
    __tablename__ = "sucursal"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    id_taller = Column(String(10), ForeignKey("public.taller.cod"), nullable=False)
    
    nombre = Column(String(255), nullable=False)
    direccion = Column(String(500), nullable=False)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    estado = Column(String(20), nullable=False, default="ACTIVO")
    
    # Relaciones
    taller = relationship("Taller", back_populates="sucursales")
