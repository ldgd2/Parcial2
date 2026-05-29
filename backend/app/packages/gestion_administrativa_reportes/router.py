from fastapi import APIRouter

from app.packages.gestion_administrativa_reportes.modules.pagos.routers.cu05_pagos import router as cu05_router
from app.packages.gestion_administrativa_reportes.modules.pagos.routers.cu17_facturacion import router as cu17_router
from app.packages.gestion_administrativa_reportes.modules.reportes_kpis.routers.cu18_reportes import router as cu18_router

router = APIRouter()

router.include_router(cu05_router, tags=["Pagos"])
router.include_router(cu17_router, tags=["Facturacion"])
router.include_router(cu18_router, tags=["Reportes"])
