from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.generic_model import GenericModel
class MetodoPago(GenericModel):
    __tablename__ = "metodo_pago"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("public.cliente.id"), nullable=False)
    stripe_payment_method_id = Column(String(255), nullable=False, unique=True)
    marca = Column(String(50), nullable=True)  # visa, mastercard, etc.
    ultimo4 = Column(String(4), nullable=True)
    es_predeterminado = Column(Boolean, default=False)

    # Relaciones
    cliente = relationship("Cliente")
