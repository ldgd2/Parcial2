from pydantic import BaseModel
from typing import Optional

class VehiculoBase(BaseModel):
    placa: str
    marca: str
    modelo: str
    anio: int
    idCliente: int

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoUpdate(VehiculoBase):
    placa: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    idCliente: Optional[int] = None

class VehiculoOut(VehiculoBase):
    pass

    class Config:
        from_attributes = True
