from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.catalogos import EspecialidadOut

class TecnicoBase(BaseModel):
    nombre: str
    correo: EmailStr
    telefono: str
    idTaller: str
    idSucursal: Optional[int] = None

class TecnicoCreate(TecnicoBase):
    contrasena: str

class TecnicoUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    contrasena: Optional[str] = None
    telefono: Optional[str] = None
    idTaller: Optional[str] = None
    idSucursal: Optional[int] = None
    estado: Optional[str] = None

class TecnicoOut(TecnicoBase):
    id: int
    estado: str
    especialidades: list[EspecialidadOut] = []

    class Config:
        from_attributes = True
