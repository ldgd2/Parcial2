from pydantic import BaseModel, Field
from typing import Optional

class SucursalBase(BaseModel):
    nombre: str = Field(..., max_length=255)
    direccion: str = Field(..., max_length=500)
    latitud: Optional[float] = None
    longitud: Optional[float] = None

class SucursalCreate(SucursalBase):
    id_taller: str = Field(..., max_length=10)

class SucursalUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=255)
    direccion: Optional[str] = Field(None, max_length=500)
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    estado: Optional[str] = Field(None, max_length=20)

class SucursalOut(SucursalBase):
    id: int
    id_taller: str
    estado: str

    class Config:
        from_attributes = True

class SucursalAdminCreate(BaseModel):
    nombre: str = Field(..., max_length=255)
    apellido: str = Field(..., max_length=255)
    correo: str = Field(..., max_length=255)
    contrasena: str = Field(..., max_length=255)
    id_taller: str = Field(..., max_length=10)

class UsuarioOut(BaseModel):
    id: int
    nombre: str
    apellido: str
    correo: str
    idTaller: str
    idSucursal: Optional[int]

    class Config:
        from_attributes = True
