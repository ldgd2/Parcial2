from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.dependencies import get_current_user, require_role
from app.packages.gestion_usuarios_seguridad.modules.tenants.schemas.sucursal_schema import UsuarioOut
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.calificacion_schema import (
    CalificacionCreate, CalificacionOut, CalificacionModeradaOut, ModerarCalificacion
)
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.emergencia import EmergenciaOut
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.services.calificacion_service import CalificacionService

router = APIRouter(prefix="/calificaciones", tags=["Calificaciones"])

@router.post("/{id_emergencia}", response_model=CalificacionOut)
async def calificar_emergencia(
    id_emergencia: int,
    data: CalificacionCreate,
    current_user: UsuarioOut = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    (Cliente) Permite al cliente calificar un servicio finalizado.
    """
    return await CalificacionService.crear_calificacion(db, id_emergencia, current_user.id, data)

@router.put("/cliente/{id_calificacion}", response_model=CalificacionOut)
async def editar_calificacion(
    id_calificacion: int,
    data: CalificacionCreate,
    current_user: UsuarioOut = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    (Cliente) Permite al cliente editar su propia calificación en cualquier momento.
    """
    return await CalificacionService.editar_calificacion(db, id_calificacion, current_user.id, data)

@router.get("/mi-calificacion/{id_emergencia}", response_model=CalificacionOut)
async def obtener_mi_calificacion(
    id_emergencia: int,
    current_user: UsuarioOut = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    (Cliente) Retorna la calificación que el cliente ya hizo para esta emergencia, si existe.
    """
    return await CalificacionService.obtener_calificacion_cliente(db, id_emergencia, current_user.id)

@router.get("/pendientes", response_model=List[EmergenciaOut])
async def obtener_pendientes(
    current_user: UsuarioOut = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    (Cliente) Retorna las emergencias finalizadas que el cliente aún no ha calificado.
    """
    return await CalificacionService.listar_pendientes_cliente(db, current_user.id)

@router.get("/taller", response_model=List[CalificacionModeradaOut])
async def obtener_calificaciones_taller(
    current_user: UsuarioOut = Depends(require_role("admin", "supervisor")),
    db: AsyncSession = Depends(get_db)
):
    """
    (Taller Admin) Retorna todas las calificaciones recibidas por el taller actual.
    """
    return await CalificacionService.listar_calificaciones_taller(db, current_user.idTaller)

@router.get("/publicas/{id_taller}", response_model=List[CalificacionModeradaOut])
async def obtener_calificaciones_publicas(
    id_taller: str,
    db: AsyncSession = Depends(get_db)
):
    """
    (Público) Retorna todas las calificaciones con estado PUBLICADA de un taller.
    Oculta los datos sensibles pero devuelve el promedio y el comentario.
    """
    return await CalificacionService.listar_calificaciones_taller(db, id_taller, solo_publicas=True)

@router.patch("/{id_calificacion}/moderar", response_model=CalificacionOut)
async def moderar_calificacion(
    id_calificacion: int,
    data: ModerarCalificacion,
    current_user: UsuarioOut = Depends(require_role("admin", "supervisor")),
    db: AsyncSession = Depends(get_db)
):
    """
    (Taller Admin) Permite ocultar comentarios inapropiados.
    """
    return await CalificacionService.moderar_calificacion(db, id_calificacion, data, current_user.idTaller)
