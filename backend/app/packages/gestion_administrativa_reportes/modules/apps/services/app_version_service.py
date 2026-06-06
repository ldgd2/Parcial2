import os
import shutil
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.packages.gestion_administrativa_reportes.modules.apps.repositories.app_version_repo import AppVersionRepository
from app.packages.gestion_administrativa_reportes.modules.apps.schemas.app_version import AppVersionCreate, AppVersionOut
from app.packages.gestion_administrativa_reportes.modules.apps.models.app_version import AppVersion

# Directorio donde se guardarán los APKs
APPS_DIR = os.path.join(os.getcwd(), "static", "apps")
os.makedirs(APPS_DIR, exist_ok=True)

class AppVersionService:
    def __init__(self, db: AsyncSession):
        self.repo = AppVersionRepository(db)

    async def publish_version(self, version: str, changelog: str, file: UploadFile) -> AppVersion:
        # Validar si ya existe
        existing = await self.repo.get_all()
        for v in existing:
            if v.version == version:
                raise HTTPException(status_code=400, detail="Esta versión ya ha sido publicada.")

        # Guardar archivo físicamente
        filename = f"tallermovil_v{version}.apk"
        file_path = os.path.join(APPS_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Base de datos relative path
        relative_path = f"/static/apps/{filename}"

        # Inactivar las versiones anteriores
        for v in existing:
            v.is_active = False

        nuevo = AppVersion(
            version=version,
            changelog=changelog,
            file_path=relative_path,
            is_active=True
        )
        self.repo.db.add(nuevo)
        await self.repo.db.commit()
        await self.repo.db.refresh(nuevo)

        return nuevo

    async def get_latest(self) -> AppVersion:
        latest = await self.repo.get_latest()
        if not latest:
            raise HTTPException(status_code=404, detail="No hay versiones publicadas.")
        return latest

    async def get_history(self) -> list[AppVersion]:
        return await self.repo.get_history()
