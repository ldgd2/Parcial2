from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.dependencies import require_role, get_current_user
from app.packages.gestion_usuarios_seguridad.modules.tenants.schemas.usuario_tenant import (
    UsuarioTenantCreate, UsuarioTenantStatus, UsuarioTenantResetPassword, UsuarioTenantOut
)
from app.packages.gestion_usuarios_seguridad.modules.tenants.services import usuario_tenant_service

router = APIRouter()

def get_admin_taller(current_user: dict = Depends(require_role("admin", "admin_sucursal"))):
    if not current_user.get("taller"):
        raise HTTPException(status_code=403, detail="El usuario no tiene un taller asociado.")
    return current_user

@router.get("/", response_model=List[UsuarioTenantOut])
async def listar_usuarios_tenant(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_taller)
):
    """Lista todos los usuarios (técnicos y administrativos) del taller actual."""
    return await usuario_tenant_service.get_all_users_for_tenant(db, current_user["taller"])

@router.post("/", response_model=UsuarioTenantOut)
async def crear_usuario_tenant(
    data: UsuarioTenantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_taller)
):
    """Crea un usuario o técnico en el taller actual."""
    # Validación de creación de usuarios para admin_sucursal
    if current_user.get("role") == "admin_sucursal":
        from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.permisos import Rol
        rol_obj = await db.get(Rol, data.rol_id)
        if not rol_obj or rol_obj.nombre not in ["MECANICO", "TECNICO"]:
            raise HTTPException(status_code=403, detail="Los administradores de sucursal solo pueden crear Técnicos o Mecánicos.")
        
        # Opcional: forzar que la sucursal del nuevo usuario sea la misma del admin_sucursal
        if current_user.get("sucursal"):
            data.sucursal_id = current_user["sucursal"]

    return await usuario_tenant_service.crear_usuario_tenant(data, db, current_user["taller"])

@router.patch("/{tipo}/{id}/status")
async def cambiar_estado(
    tipo: str,
    id: int,
    data: UsuarioTenantStatus,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_taller)
):
    """Suspende o activa un usuario."""
    if tipo not in ["TECNICO", "ADMINISTRATIVO"]:
        raise HTTPException(status_code=400, detail="Tipo inválido")
    return await usuario_tenant_service.actualizar_estado_usuario(id, tipo, data, db, current_user["taller"])

@router.patch("/{tipo}/{id}/reset-password")
async def reset_password(
    tipo: str,
    id: int,
    data: UsuarioTenantResetPassword,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_taller)
):
    """Restablece la contraseña de un usuario."""
    if tipo not in ["TECNICO", "ADMINISTRATIVO"]:
        raise HTTPException(status_code=400, detail="Tipo inválido")
    return await usuario_tenant_service.resetear_contrasena_usuario(id, tipo, data, db, current_user["taller"])

# Agregamos endpoint para consultar ROLES del tenant
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.permisos import Rol
from sqlalchemy import select
from pydantic import BaseModel

class RolOut(BaseModel):
    id: int
    nombre: str

@router.get("/roles", response_model=List[RolOut])
async def obtener_roles_disponibles(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_admin_taller)
):
    # En la base de datos están SUPER_ADMIN, ADMIN_TALLER, ADMIN_SUCURSAL, SUPERVISOR, OPERADOR, MECANICO, CLIENTE
    if current_user.get("role") == "admin_sucursal":
        roles_permitidos = ["MECANICO"]
    else:
        # Retornaremos solo los que puede crear: SUPERVISOR, OPERADOR, MECANICO, ADMIN_SUCURSAL
        roles_permitidos = ["SUPERVISOR", "OPERADOR", "MECANICO", "ADMIN_SUCURSAL"]
        
    stmt = select(Rol).where(Rol.nombre.in_(roles_permitidos))
    roles = (await db.execute(stmt)).scalars().all()
    return [{"id": r.id, "nombre": r.nombre} for r in roles]
