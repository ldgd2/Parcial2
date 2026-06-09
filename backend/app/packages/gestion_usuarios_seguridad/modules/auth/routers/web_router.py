"""
CU01 — Gestionar Inicio de Sesión
CU02 — Gestionar Cierre de Sesión

POST /auth/register       → Registro de Administrador y Taller
POST /auth/login          → CU01 Inicio de sesión (App Móvil — Cliente/Técnico)
POST /auth/login/web      → CU01 Inicio de sesión (Portal Web — Admin)
POST /auth/logout         → CU02 Cierre de sesión
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.packages.gestion_usuarios_seguridad.modules.auth.schemas.auth import LoginRequest, TokenResponse, RegisterAdminRequest
from app.packages.gestion_usuarios_seguridad.modules.auth.services import auth_service

router = APIRouter(prefix="/auth", tags=["GPS — Autenticación (CU01/CU02)"])


@router.post("/register", summary="Registro de Administrador y Taller")
async def register(data: RegisterAdminRequest, db: AsyncSession = Depends(get_db)):
    """
    Registra un Administrador de Taller junto con su taller inicial.
    """
    return await auth_service.register_admin(data, db)


@router.post("/login", response_model=TokenResponse, summary="CU01 — Inicio de sesión Móvil (Cliente/Técnico)")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Autentica un Cliente o Técnico (Uso exclusivo para la App Móvil).
    - **rol**: `"cliente"` o `"tecnico"`
    """
    return await auth_service.login(data, db)


@router.post("/login/web", response_model=TokenResponse, summary="CU01 — Inicio de sesión Web (Admin)")
async def login_web(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Autentica un Administrador de Taller (Uso exclusivo para el Portal Web).
    - **rol**: `"admin"`
    """
    return await auth_service.login_web(data, db)


@router.post("/logout", summary="CU02 — Cierre de sesión")
async def logout():
    """
    El cliente descarta el token. En una implementación con lista negra
    (blacklist) de JWT, aquí se agregaría el jti a Redis.
    """
    return {"message": "Sesión cerrada correctamente. Descarte el token en el cliente."}

from app.packages.gestion_usuarios_seguridad.modules.auth.schemas.auth import AuthMeResponse
from pydantic import BaseModel
from typing import List
from sqlalchemy import select
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.suscripcion import PlanSuscripcion

@router.get("/me", response_model=AuthMeResponse, summary="Obtener detalles del usuario y sus permisos/suscripción actual")
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna el estado de la cuenta, plan de suscripción actual y la lista consolidada de permisos.
    """
    return await auth_service.get_me(current_user, db)


class PublicPlanOut(BaseModel):
    id: int
    nombre: str
    descripcion: str | None = None
    precio_mensual: float
    max_sucursales: int
    max_tecnicos: int
    max_admins_sucursal: int

@router.get("/planes", response_model=List[PublicPlanOut], summary="Obtener planes de suscripción públicos")
async def get_public_planes(db: AsyncSession = Depends(get_db)):
    """
    Retorna los planes de suscripción disponibles para el registro de nuevos talleres.
    """
    planes = (await db.execute(select(PlanSuscripcion).order_by(PlanSuscripcion.precio_mensual))).scalars().all()
    return planes
