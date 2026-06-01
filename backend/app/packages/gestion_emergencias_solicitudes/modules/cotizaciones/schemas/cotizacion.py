from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CotizacionBase(BaseModel):
    descripcion_servicio: str
    costo_mano_obra: float
    costo_repuestos: float = 0.0
    tiempo_estimado_horas: int
    condiciones: Optional[str] = None

class CotizacionCreate(CotizacionBase):
    pass

class CotizacionUpdate(BaseModel):
    estado: str
    condiciones: Optional[str] = None

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
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    taller: Optional[TallerInfo] = None

    class Config:
        from_attributes = True
