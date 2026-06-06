from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CalificacionCreate(BaseModel):
    puntuacion_taller: int = Field(..., ge=1, le=5, description="Puntuación de 1 a 5 para el taller")
    puntuacion_tecnico: int = Field(..., ge=1, le=5, description="Puntuación de 1 a 5 para el técnico")
    comentario: Optional[str] = Field(None, max_length=500)

class CalificacionOut(BaseModel):
    id: int
    idEmergencia: int
    idCliente: int
    idTaller: str
    idTecnico: int
    puntuacion_taller: int
    puntuacion_tecnico: int
    comentario: Optional[str]
    estado: str
    fecha: datetime

    class Config:
        from_attributes = True

class CalificacionModeradaOut(CalificacionOut):
    # En la vista del admin, podemos mandar nombres
    cliente_nombre: Optional[str] = None
    tecnico_nombre: Optional[str] = None

class ModerarCalificacion(BaseModel):
    estado: str = Field(..., description="PUBLICADA o OCULTADA")
