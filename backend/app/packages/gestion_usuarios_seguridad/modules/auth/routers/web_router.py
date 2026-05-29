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
