from fastapi import APIRouter

from app.packages.gestion_administrativa_reportes.modules.pagos.routers.cu05_pagos import router as cu05_router
from app.packages.gestion_administrativa_reportes.modules.pagos.routers.cu17_facturacion import router as cu17_router
from app.packages.gestion_administrativa_reportes.modules.reportes_kpis.routers.cu18_reportes import router as cu18_router

from app.packages.gestion_administrativa_reportes.modules.pagos.routers.stripe_router import router as stripe_router

from app.packages.gestion_administrativa_reportes.modules.apps.routers.app_version_router import router as app_version_router

router = APIRouter()

router.include_router(cu05_router, tags=["Pagos"])
router.include_router(stripe_router, tags=["Pagos"])
router.include_router(cu17_router, tags=["Facturacion"])
router.include_router(cu18_router, tags=["Reportes"])
router.include_router(app_version_router, prefix="/apps", tags=["Apps Distribucion"])
