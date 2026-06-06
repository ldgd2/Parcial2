from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioTenantCreate(BaseModel):
    nombre: str
    apellido: Optional[str] = ""
    correo: EmailStr
    contrasena: str
    telefono: Optional[str] = None # Solo requerido si es tecnico
    rol_id: int
    sucursal_id: Optional[int] = None

class UsuarioTenantUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    rol_id: Optional[int] = None
    sucursal_id: Optional[int] = None

class UsuarioTenantStatus(BaseModel):
    estado: str

class UsuarioTenantResetPassword(BaseModel):
    nueva_contrasena: str

class UsuarioTenantOut(BaseModel):
    id: int
    nombre: str
    apellido: Optional[str] = None
    correo: str
    telefono: Optional[str] = None
    estado: str
    tipo: str # "TECNICO" o "ADMINISTRATIVO"
    rol_nombre: str
    sucursal_id: Optional[int] = None
    
    class Config:
        from_attributes = True
