from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MensajeChatBase(BaseModel):
    contenido: Optional[str] = None
    imagen_url: Optional[str] = None
    audio_url: Optional[str] = None

class MensajeChatCreate(MensajeChatBase):
    pass

class MensajeChatOut(MensajeChatBase):
    id: int
    idEmergencia: int
    remitente_id: int
    rol_remitente: str
    fecha_envio: datetime

    class Config:
        from_attributes = True
