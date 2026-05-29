from pydantic import BaseModel
from typing import Optional

class MetodoPagoBase(BaseModel):
    marca: Optional[str] = None
    ultimo4: Optional[str] = None
    es_predeterminado: bool = False

class MetodoPagoCreate(BaseModel):
    stripe_payment_method_id: str

class MetodoPagoOut(MetodoPagoBase):
    id: int
    stripe_payment_method_id: str

    class Config:
        from_attributes = True

class SetupIntentOut(BaseModel):
    client_secret: str
    customer_id: str
