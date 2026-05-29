from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.catalogos import EspecialidadOut


# ─── Taller ───────────────────────────────────────────────────────

class TallerCreate(BaseModel):
    nombre: str
    direccion: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None


class TallerUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    estado: Optional[str] = None  # "ACTIVO" | "INACTIVO"
    especialidades: Optional[List[int]] = None # IDs


class TallerOut(BaseModel):
    cod: str
    nombre: str
    direccion: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    estado: str
    id_admin: Optional[int] = None
    especialidades: List[EspecialidadOut] = []

    model_config = {"from_attributes": True}


# ─── Disponibilidad (CU06) ────────────────────────────────────────

class DisponibilidadUpdate(BaseModel):
    estado: str  # "ACTIVO" | "INACTIVO"
