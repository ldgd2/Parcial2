from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db.repository import BaseRepository
from app.packages.gestion_administrativa_reportes.modules.reportes_kpis.models.bitacora import Bitacora

class BitacoraCreate(BaseModel):
    idUsuario: Optional[int] = None
    accion: str
    tabla: str
    registro_id: str
    detalles: Optional[dict] = None
    ip: str

class BitacoraUpdate(BaseModel):
    pass

class BitacoraRepository(BaseRepository[Bitacora, BitacoraCreate, BitacoraUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Bitacora, db)

