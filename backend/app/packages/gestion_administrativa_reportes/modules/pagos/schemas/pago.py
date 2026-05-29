from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import Optional, List

class FacturaItem(BaseModel):
    descripcion: str
    tipo: str  # 'servicio' o 'repuesto'
    cantidad: int
    precio_unitario: float
    total: float

class DetalleFactura(BaseModel):
    items: List[FacturaItem]
    subtotal: float
    impuestos: float
    total_general: float

class PagoBase(BaseModel):
    monto: Decimal
    monto_comision: Decimal
    cliente_id: int
    emergencia_id: int

class PagoCreate(BaseModel):
    monto: Decimal
    emergencia_id: int

class PagoStripeCreate(BaseModel):
    emergencia_id: int
    metodo_pago_id: Optional[str] = None # Si es None, se asume que se añadirá una nueva tarjeta
    monto: Decimal

class PagoOut(PagoBase):
    id: int
    fecha_pago: date
    stripe_intent_id: Optional[str]
    estado: str
    metodo_pago_id: Optional[str]
    detalle_factura: Optional[dict]

    class Config:
        from_attributes = True
