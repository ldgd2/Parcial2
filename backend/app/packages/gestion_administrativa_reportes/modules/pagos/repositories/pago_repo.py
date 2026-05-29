from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.db.repository import BaseRepository
from app.packages.gestion_administrativa_reportes.modules.pagos.models.pago import Pago

class PagoCreate(BaseModel):
    monto: float
    monto_comision: float
    cliente_id: int
    emergencia_id: int
    estado: str
    detalle_factura: Optional[dict] = None

class PagoUpdate(BaseModel):
    pass

class PagoRepository(BaseRepository[Pago, PagoCreate, PagoUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Pago, db)
