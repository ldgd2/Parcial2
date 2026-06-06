from fastapi import APIRouter

# Import sub-routers
from app.packages.gestion_usuarios_seguridad.modules.auth.routers.web_router import router as auth_router
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.routers.cu07_cu13_tecnicos import router as tecnicos_router
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.routers.cu06_disponibilidad import router as disponibilidad_router
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.routers.api_router import router as usuarios_vehiculos_router
from app.packages.gestion_usuarios_seguridad.modules.tenants.routers.sucursal_router import router as sucursal_router
from app.packages.gestion_usuarios_seguridad.modules.tenants.routers.saas_router import router as saas_router
from app.packages.gestion_usuarios_seguridad.modules.tenants.routers.usuario_tenant_router import router as usuario_tenant_router

router = APIRouter()

# Incluir los sub-routers
router.include_router(auth_router)
router.include_router(usuarios_vehiculos_router)
router.include_router(tecnicos_router)
router.include_router(disponibilidad_router)
router.include_router(sucursal_router, prefix="/sucursales", tags=["Sucursales"])
router.include_router(saas_router, prefix="/saas/tenants", tags=["SaaS Tenants"])
router.include_router(usuario_tenant_router, prefix="/usuarios-tenant", tags=["Usuarios (Tenant)"])
