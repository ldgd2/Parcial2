from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel
class HistorialEstado(GenericModel):
    __tablename__ = "historial_estado"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    fecha_cambio = Column("fechaCambio", DateTime(timezone=True), nullable=False, server_default=func.now())
    idEmergencia = Column(Integer, ForeignKey("public.emergencia.id"), nullable=False, index=True)
    idEstado = Column(Integer, ForeignKey("public.estado.id"), nullable=False)

    emergencia = relationship("Emergencia", back_populates="historial")
    estado = relationship("Estado")
