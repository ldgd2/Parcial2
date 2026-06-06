from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.db.repository import BaseRepository
from app.packages.gestion_administrativa_reportes.modules.apps.models.app_version import AppVersion
from app.packages.gestion_administrativa_reportes.modules.apps.schemas.app_version import AppVersionCreate

class AppVersionRepository(BaseRepository[AppVersion, AppVersionCreate, AppVersionCreate]):
    def __init__(self, db: Session):
        super().__init__(model=AppVersion, db=db)

    async def get_latest(self) -> AppVersion:
        result = await self.db.execute(
            select(self.model)
            .where(self.model.is_active == True)
            .order_by(desc(self.model.release_date))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_history(self) -> list[AppVersion]:
        result = await self.db.execute(
            select(self.model)
            .order_by(desc(self.model.release_date))
        )
        return result.scalars().all()
