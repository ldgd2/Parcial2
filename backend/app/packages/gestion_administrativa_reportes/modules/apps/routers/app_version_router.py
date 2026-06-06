import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.packages.gestion_administrativa_reportes.modules.apps.schemas.app_version import AppVersionOut
from app.packages.gestion_administrativa_reportes.modules.apps.services.app_version_service import AppVersionService

router = APIRouter()

@router.post("/publish", response_model=AppVersionOut, summary="Publicar nueva versión de la App")
async def publish_app(
    version: str = Form(...),
    changelog: str = Form(""),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    service = AppVersionService(db)
    return await service.publish_version(version, changelog, file)

@router.get("/latest", response_model=AppVersionOut, summary="Obtener metadatos de la última versión")
async def get_latest_app(db: AsyncSession = Depends(get_db)):
    service = AppVersionService(db)
    return await service.get_latest()

@router.get("/history", response_model=list[AppVersionOut], summary="Obtener historial de versiones")
async def get_app_history(db: AsyncSession = Depends(get_db)):
    service = AppVersionService(db)
    return await service.get_history()

@router.get("/download/latest", summary="Descargar directamente la última versión (APK)")
async def download_latest_app(db: AsyncSession = Depends(get_db)):
    service = AppVersionService(db)
    latest = await service.get_latest()
    
    # latest.file_path es "/static/apps/tallermovil_v1.0.0.apk"
    # convertir a ruta absoluta
    base_dir = os.getcwd()
    # file_path_abs = base_dir + latest.file_path  (cuidado con la barra inicial)
    relative = latest.file_path.lstrip("/") # "static/apps/tallermovil_v1.0.0.apk"
    absolute_path = os.path.join(base_dir, relative)
    
    if not os.path.exists(absolute_path):
        raise HTTPException(status_code=404, detail="Archivo APK no encontrado físicamente.")
        
    return FileResponse(
        absolute_path, 
        media_type="application/vnd.android.package-archive",
        filename=os.path.basename(absolute_path)
    )
