from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Callable, Any

from app.db.session import get_db
from app.core.security import decode_access_token
# You might have a get_current_user dependency elsewhere, but we assume we decode the token here
# We need to know who the user is: Admin, Tecnico, or Cliente?
# We will just write the logic assuming we have user context.

from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.permisos import Permiso, Rol, RolPermiso, PlanPermiso
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.suscripcion import PlanSuscripcion
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.usuario import Usuario

from app.core.dependencies import get_current_user

def require_permission(required_codigo: str) -> Callable:
    """
    Dependencia de FastAPI para verificar si el usuario tiene el permiso dado.
    Considera si el usuario es un Admin de Taller (verificando la suscripción)
    o un Cliente/Mecánico (verificando solo sus roles base).
    """
    async def permission_checker(
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        # Mapeamos los roles del JWT a los nombres de la base de datos
        role_map = {
            "taller": "ADMIN_TALLER",
            "tecnico": "MECANICO",
            "cliente": "CLIENTE"
        }
        
        raw_role = current_user.get("role", "")
        user_role = role_map.get(raw_role, raw_role)
        taller_cod = current_user.get("taller_cod") or current_user.get("idTaller")
        
        if user_role in ["MECANICO", "CLIENTE"]:
            # Verificar si el rol tiene el permiso asociado
            stmt = select(Permiso).join(RolPermiso).join(Rol).where(
                Rol.nombre == user_role,
                Permiso.codigo == required_codigo
            )
            permiso = await db.execute(stmt)
            if not permiso.scalar_one_or_none():
                raise HTTPException(status_code=403, detail="No tienes permisos suficientes.")
            return True

        elif user_role == "ADMIN_TALLER":
            if not taller_cod:
                raise HTTPException(status_code=403, detail="No se identificó el taller asociado.")
                
            # Verificar en Rol de Admin
            stmt_rol = select(Permiso).join(RolPermiso).join(Rol).where(
                Rol.nombre == user_role,
                Permiso.codigo == required_codigo
            )
            has_role_perm = (await db.execute(stmt_rol)).scalar_one_or_none()

            # Verificar en Plan de Suscripción del Taller
            stmt_plan = select(Permiso).join(PlanPermiso).join(PlanSuscripcion).join(Taller).where(
                Taller.cod == taller_cod,
                Permiso.codigo == required_codigo
            )
            has_plan_perm = (await db.execute(stmt_plan)).scalar_one_or_none()

            if not has_role_perm or not has_plan_perm:
                raise HTTPException(
                    status_code=403, 
                    detail="Tu plan de suscripción no incluye este permiso o tu rol no lo permite."
                )
            return True

        raise HTTPException(status_code=403, detail="Acceso denegado.")
        
    return permission_checker


async def check_sucursal_limit(taller_cod: str, db: AsyncSession):
    """
    Verifica si el taller ya alcanzó el límite de sucursales de su plan.
    """
    from sqlalchemy import func
    from app.packages.gestion_usuarios_seguridad.modules.tenants.models.sucursal import Sucursal

    # Obtener el plan del taller
    taller = await db.get(Taller, taller_cod)
    if not taller or not taller.plan_id:
        return # Sin plan = Sin límite u error. Mejor asumir gratuito = 1.
        
    plan = await db.get(PlanSuscripcion, taller.plan_id)
    if not plan:
        return
        
    # Contar sucursales actuales
    stmt = select(func.count()).select_from(Sucursal).where(Sucursal.id_taller == taller_cod)
    count = (await db.execute(stmt)).scalar()

    if count >= plan.max_sucursales:
        raise HTTPException(
            status_code=403, 
            detail=f"Has alcanzado el límite de {plan.max_sucursales} sucursales de tu plan '{plan.nombre}'."
        )
