from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time, datetime
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.schemas.tecnico import TecnicoOut
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.schemas.vehiculo import VehiculoOut
from app.packages.gestion_administrativa_reportes.modules.pagos.schemas.pago import PagoOut

# ─── Resumen IA ───────────────────────────────────────────────────

class ResumenIAOut(BaseModel):
    id: int
    resumen: str
    ficha_tecnica: Optional[dict] = None

    class Config:
        from_attributes = True

# ─── Crear emergencia ─────────────────────────────────────────────

class EmergenciaCreate(BaseModel):
    descripcion: str
    texto_adicional: Optional[str] = None
    direccion: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    hora: time
    placaVehiculo: str
    audio_url: Optional[str] = None
    evidencias_urls: List[str] = []

# ─── Respuesta emergencia ─────────────────────────────────────────

class EmergenciaOut(BaseModel):
    id: int
    descripcion: str
    texto_adicional: Optional[str]
    direccion: str
    latitud: Optional[float]
    longitud: Optional[float]
    fecha: date
    hora: time
    idTaller: Optional[str] = None
    idPrioridad: int
    idCategoria: int
    placaVehiculo: str
    audio_url: Optional[str] = None
    estado_actual: Optional[str] = None   # Calculado desde historial
    is_locked: Optional[bool] = False    # Para el mutex dinámico
    
    # Datos detallados
    resumen_ia: Optional[ResumenIAOut] = None
    evidencias: List['EvidenciaOut'] = []
    tecnicos_asignados: List[TecnicoOut] = []
    vehiculo: Optional[VehiculoOut] = None
    pago: Optional[PagoOut] = None

    model_config = {"from_attributes": True}


# ─── Actualizar estado (CU15 — Taller) ───────────────────────────

class ActualizarEstadoRequest(BaseModel):
    idEstado: int
    comentario: Optional[str] = None

class FinalizarEmergenciaRequest(BaseModel):
    monto_total: float
    comentarios_finales: Optional[str] = None


# ─── Evidencia ────────────────────────────────────────────────────

class EvidenciaOut(BaseModel):
    id: int
    direccion: str
    idEmergencia: int

    model_config = {"from_attributes": True}

# Resolver referencias circulares si las hubiera
EmergenciaOut.model_rebuild()
