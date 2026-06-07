from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.usuario import Usuario
from app.packages.gestion_emergencias_solicitudes.modules.cotizaciones.schemas.cotizacion import CotizacionCreate, CotizacionUpdate, CotizacionOut, CotizacionAjuste
from app.packages.gestion_emergencias_solicitudes.modules.cotizaciones.services.cotizacion_service import CotizacionService

router = APIRouter(prefix="/cotizaciones", tags=["Cotizaciones"])

@router.put("/{id_cotizacion}/ajustar", response_model=CotizacionOut)
async def ajustar_cotizacion(
    id_cotizacion: int,
    data: CotizacionAjuste,
    db: Session = Depends(get_db)
):
    """(Técnico) Ajusta los productos y servicios de la cotización en el sitio."""
    service = CotizacionService(db)
    return await service.ajustar_cotizacion_async(id_cotizacion, data)

@router.post("/{id_emergencia}", response_model=CotizacionOut)
async def create_cotizacion(
    id_emergencia: int,
    data: CotizacionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """(Taller) Crea una cotización para una emergencia."""
    service = CotizacionService(db)
    # Extraemos el cod del Taller del token del usuario autenticado
    id_taller = current_user.get("taller", "TALLER_001") if current_user else "TALLER_001"
    return await service.create_cotizacion(id_emergencia, id_taller, data)

@router.get("/emergencia/{id_emergencia}", response_model=list[CotizacionOut])
async def get_cotizaciones_by_emergencia(
    id_emergencia: int,
    db: Session = Depends(get_db)
):
    """Obtiene todas las cotizaciones hechas para una emergencia."""
    service = CotizacionService(db)
    return await service.get_cotizaciones_by_emergencia(id_emergencia)

@router.put("/{id_cotizacion}/estado", response_model=CotizacionOut)
async def update_estado_cotizacion(
    id_cotizacion: int,
    data: CotizacionUpdate,
    db: Session = Depends(get_db)
):
    """(Cliente/Taller) Actualiza el estado (ACEPTADA, RECHAZADA) o re-negocia."""
    service = CotizacionService(db)
    return await service.update_estado_async(id_cotizacion, data)
