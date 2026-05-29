from fastapi import APIRouter

from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.routers.cu04_cu08_cu09_reportar import router as cu04_router
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.routers.cu10_ficha_tecnica import router as cu10_router
from app.packages.inteligencia_artificial_automatizacion.modules.asignacion.routers.cu11_motor_asignacion import router as cu11_router
from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.routers.cu12_notificaciones_ia import router as cu12_router
from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.routers.cu16_chat import router as cu16_router
from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.routers.ws import router as ws_router

router = APIRouter()

router.include_router(cu04_router, tags=["IA - Reportar"])
router.include_router(cu10_router, tags=["IA - Ficha Tecnica"])
router.include_router(cu11_router, tags=["IA - Asignacion"])
router.include_router(cu12_router, tags=["Notificaciones"])
router.include_router(cu16_router, tags=["Chat"])
router.include_router(ws_router, tags=["WebSockets"])
