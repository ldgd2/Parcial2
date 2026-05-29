from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, func, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class Pago(Base):
    __tablename__ = "pago"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    emergencia_id = Column(Integer, ForeignKey("emergencia.id"), nullable=False)
    
    monto = Column("Monto", Numeric(18, 2), nullable=False)
    monto_comision = Column("MontoComision", Numeric(18, 2), nullable=False)
    
    stripe_intent_id = Column(String(255), nullable=True)
    metodo_pago_id = Column(String(255), nullable=True) # Payment Method ID
    estado = Column(String(50), nullable=False, server_default="PENDIENTE") # PENDIENTE, COMPLETADO, FALLIDO
    
    detalle_factura = Column(JSON, nullable=True)
    
    fecha_pago = Column("fechaPago", Date, nullable=False, server_default=func.current_date())

    # Relaciones
    cliente = relationship("Cliente", foreign_keys=[cliente_id])
    emergencia = relationship("Emergencia", foreign_keys=[emergencia_id], back_populates="pago")
