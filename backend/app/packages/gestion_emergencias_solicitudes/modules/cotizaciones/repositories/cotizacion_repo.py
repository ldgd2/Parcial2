from sqlalchemy.orm import Session, joinedload
from app.db.repository import BaseRepository
from app.packages.gestion_emergencias_solicitudes.modules.cotizaciones.models.cotizacion import Cotizacion
from app.packages.gestion_emergencias_solicitudes.modules.cotizaciones.schemas.cotizacion import CotizacionCreate, CotizacionUpdate

class CotizacionRepository(BaseRepository[Cotizacion, CotizacionCreate, CotizacionUpdate]):
    def __init__(self, db: Session):
        super().__init__(model=Cotizacion, db=db)
        
    def get_by_emergencia(self, id_emergencia: int):
        return self.db.query(self.model).options(joinedload(self.model.taller)).filter(self.model.idEmergencia == id_emergencia).all()

        
    def get_by_emergencia_and_taller(self, id_emergencia: int, id_taller: str):
        return self.db.query(self.model).filter(
            self.model.idEmergencia == id_emergencia,
            self.model.idTaller == id_taller
        ).first()
