from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.packages.gestion_usuarios_seguridad.modules.tenants.schemas.sucursal_schema import SucursalCreate, SucursalUpdate, SucursalOut
from app.packages.gestion_usuarios_seguridad.modules.tenants.services import sucursal_service

router = APIRouter()

@router.post("/", response_model=SucursalOut, status_code=status.HTTP_201_CREATED)
async def crear_sucursal(
    data: SucursalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Validar permisos
    if current_user.get("role") == "admin_sucursal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Los administradores de sucursal no pueden crear sucursales.")
    
    if "PERMISO_GESTIONAR_SUCURSALES" not in current_user.get("permisos", []) and "ALL_PERMISSIONS_FALLBACK_IF_ANY" not in current_user.get("permisos", []):
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes.")
            
    return await sucursal_service.crear_sucursal(data, db)

@router.get("/taller/{id_taller}", response_model=List[SucursalOut])
async def obtener_sucursales_de_taller(
    id_taller: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Validar que si es un admin_sucursal, solo vea las de su taller o las asignadas
    return await sucursal_service.obtener_sucursales_taller(id_taller, db)

@router.put("/{sucursal_id}", response_model=SucursalOut)
async def actualizar_sucursal(
    sucursal_id: int,
    data: SucursalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await sucursal_service.actualizar_sucursal(sucursal_id, data, db)

@router.delete("/{sucursal_id}", response_model=SucursalOut)
async def eliminar_sucursal(
    sucursal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await sucursal_service.desactivar_sucursal(sucursal_id, db)

from app.packages.gestion_usuarios_seguridad.modules.tenants.schemas.sucursal_schema import SucursalAdminCreate, UsuarioOut

@router.post("/{sucursal_id}/admin", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
async def crear_admin_sucursal(
    sucursal_id: int,
    data: SucursalAdminCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") == "admin_sucursal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Los administradores de sucursal no pueden crear administradores.")

    if "PERMISO_GESTIONAR_SUCURSALES" not in current_user.get("permisos", []) and "ALL_PERMISSIONS_FALLBACK_IF_ANY" not in current_user.get("permisos", []):
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes para asignar un administrador.")
            
    return await sucursal_service.crear_admin_sucursal(sucursal_id, data, db)

@router.get("/taller/{id_taller}/candidatos-admin", response_model=List[UsuarioOut])
async def obtener_candidatos_admin(
    id_taller: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene usuarios del taller que pueden ser asignados como administradores de sucursal"""
    return await sucursal_service.obtener_candidatos_admin_taller(id_taller, db)

@router.put("/{sucursal_id}/asignar-admin/{usuario_id}", response_model=UsuarioOut)
async def asignar_admin_existente(
    sucursal_id: int,
    usuario_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Vincula un usuario existente a una sucursal como su administrador"""
    if current_user.get("role") == "admin_sucursal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Los administradores de sucursal no pueden asignar administradores.")

    if "PERMISO_GESTIONAR_SUCURSALES" not in current_user.get("permisos", []) and "ALL_PERMISSIONS_FALLBACK_IF_ANY" not in current_user.get("permisos", []):
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes.")
            
    return await sucursal_service.asignar_admin_existente(sucursal_id, usuario_id, db)

from pydantic import BaseModel

class EspecialidadOut(BaseModel):
    id_sucursal: int
    id_especialidad: int
    class Config:
        from_attributes = True

class SucursalEspecialidadesUpdate(BaseModel):
    especialidades_ids: List[int]

@router.get("/{sucursal_id}/especialidades", response_model=List[EspecialidadOut])
async def obtener_especialidades_de_sucursal(
    sucursal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene las especialidades asignadas a una sucursal"""
    return await sucursal_service.obtener_especialidades_sucursal(sucursal_id, db)

@router.put("/{sucursal_id}/especialidades")
async def actualizar_especialidades_de_sucursal(
    sucursal_id: int,
    data: SucursalEspecialidadesUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Actualiza las especialidades de una sucursal"""
    if current_user.get("role") == "admin_sucursal":
        if current_user.get("sucursal") != sucursal_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puede modificar las especialidades de su propia sucursal.")
    elif current_user.get("role") != "admin":
        if "PERMISO_GESTIONAR_SUCURSALES" not in current_user.get("permisos", []) and "ALL_PERMISSIONS_FALLBACK_IF_ANY" not in current_user.get("permisos", []):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes.")
            
    return await sucursal_service.actualizar_especialidades_sucursal(sucursal_id, data.especialidades_ids, db)
