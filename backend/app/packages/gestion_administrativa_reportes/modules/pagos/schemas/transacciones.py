from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, Dict

# Historial Estado
class HistorialEstadoBase(BaseModel):
    idEmergencia: int
    idEstado: int

class HistorialEstadoCreate(HistorialEstadoBase):
    pass

class HistorialEstadoOut(HistorialEstadoBase):
    id: int
    fechaCambio: datetime

    class Config:
        from_attributes = True


# Evidencia
class EvidenciaBase(BaseModel):
    direccion: str
    idEmergencia: int

class EvidenciaCreate(EvidenciaBase):
    pass

class EvidenciaOut(EvidenciaBase):
    id: int

    class Config:
        from_attributes = True


# Resumen IA (Pydantic Out format)
class ResumenIABase(BaseModel):
    resumen: str
    ficha_tecnica: Optional[Dict] = None
    idEmergencia: int

class ResumenIACreate(ResumenIABase):
    pass

class ResumenIAOut(ResumenIABase):
    id: int

    class Config:
        from_attributes = True
