from pydantic import BaseModel, EmailStr
from typing import Optional


# ─── Login ───────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str
    rol: str  # "cliente" | "tecnico" | "admin"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    user_id: int
    nombre: str
    cod_taller: Optional[str] = None
    nombre_taller: Optional[str] = None


# ─── Registro de Administrador ──────────────────────────────
class RegisterAdminRequest(BaseModel):
    # Admin info
    nombre: str
    apellido: str
    correo: EmailStr
    contrasena: str
    
    # Workshop info
    nombre_taller: str
    direccion_taller: str
    latitud_taller: Optional[float] = None
    longitud_taller: Optional[float] = None
