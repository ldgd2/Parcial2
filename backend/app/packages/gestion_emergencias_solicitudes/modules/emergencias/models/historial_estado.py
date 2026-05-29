from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class HistorialEstado(Base):
    __tablename__ = "historial_estado"

    id = Column(Integer, primary_key=True)
    fecha_cambio = Column("fechaCambio", DateTime(timezone=True), nullable=False, server_default=func.now())
    idEmergencia = Column(Integer, ForeignKey("emergencia.id"), nullable=False, index=True)
    idEstado = Column(Integer, ForeignKey("estado.id"), nullable=False)

    emergencia = relationship("Emergencia", back_populates="historial")
    estado = relationship("Estado")
