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
    if "PERMISO_GESTIONAR_SUCURSALES" not in current_user.get("permisos", []) and "ALL_PERMISSIONS_FALLBACK_IF_ANY" not in current_user.get("permisos", []):
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes para asignar un administrador.")
            
    return await sucursal_service.crear_admin_sucursal(sucursal_id, data, db)
