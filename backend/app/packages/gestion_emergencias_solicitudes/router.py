from fastapi import APIRouter

from app.packages.gestion_emergencias_solicitudes.modules.emergencias.routers.catalogos_router import router as catalogos_router
from app.packages.gestion_emergencias_solicitudes.modules.auxilio_solicitudes.routers.cu14_solicitudes_cliente import router as cu14_router
from app.packages.gestion_emergencias_solicitudes.modules.auxilio_solicitudes.routers.cu15_solicitudes_taller import router as cu15_router

router = APIRouter()

router.include_router(catalogos_router, tags=["Catalogos Transversales"])
router.include_router(cu14_router, tags=["Solicitudes - Cliente"])
router.include_router(cu15_router, tags=["Solicitudes - Taller"])
