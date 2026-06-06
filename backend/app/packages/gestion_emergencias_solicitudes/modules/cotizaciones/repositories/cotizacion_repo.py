from sqlalchemy.orm import Session, joinedload
from app.db.repository import BaseRepository
from app.packages.gestion_emergencias_solicitudes.modules.cotizaciones.models.cotizacion import Cotizacion
from app.packages.gestion_emergencias_solicitudes.modules.cotizaciones.schemas.cotizacion import CotizacionCreate, CotizacionUpdate

class CotizacionRepository(BaseRepository[Cotizacion, CotizacionCreate, CotizacionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=Cotizacion, db=db)
        
    async def get_by_emergencia(self, id_emergencia: int):
        from sqlalchemy import select
        result = await self.db.execute(select(self.model).options(joinedload(self.model.taller)).where(self.model.idEmergencia == id_emergencia))
        return result.scalars().all()

        
    async def get_by_emergencia_and_taller(self, id_emergencia: int, id_taller: str):
        from sqlalchemy import select
        result = await self.db.execute(select(self.model).where(
            self.model.idEmergencia == id_emergencia,
            self.model.idTaller == id_taller
        ))
        return result.scalar_one_or_none()
