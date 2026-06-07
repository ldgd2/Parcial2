from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from typing import Optional, List, Any

class ItemProducto(BaseModel):
    nombre: str
    precio: float
    cantidad: int

class ItemServicio(BaseModel):
    nombre: str
    precio: float

class CotizacionBase(BaseModel):
    descripcion_servicio: Optional[str] = None
    moneda: str = "BOB"
    lista_productos: List[ItemProducto] = []
    lista_servicios: List[ItemServicio] = []
    tiempo_estimado: str
    condiciones: Optional[str] = None

class CotizacionCreate(CotizacionBase):
    pass

class CotizacionUpdate(BaseModel):
    estado: str
    condiciones: Optional[str] = None

class CotizacionAjuste(BaseModel):
    lista_productos: List[ItemProducto]
    lista_servicios: List[ItemServicio]
    descripcion_servicio: Optional[str] = None

class TallerInfo(BaseModel):
    nombre: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    calificacion_promedio: Optional[float] = None

    class Config:
        from_attributes = True

class CotizacionOut(CotizacionBase):
    id: int
    idEmergencia: int
    idTaller: str
    estado: str
    subtotal_productos: float
    subtotal_servicios: float
    total_general: float
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    taller: Optional[TallerInfo] = None

    class Config:
        from_attributes = True
