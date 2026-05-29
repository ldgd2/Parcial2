from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload, joinedload
from pydantic import BaseModel
import datetime

from app.db.repository import BaseRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.historial_estado import HistorialEstado
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.categoria_problema import CategoriaProblema

class EmergenciaCreateSchema(BaseModel):
    descripcion: str
    texto_adicional: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    direccion: str
    hora: datetime.time
    placaVehiculo: str
    evidencias_urls: List[str] = []
    audio_url: Optional[str] = None

class EmergenciaUpdateSchema(BaseModel):
    pass

class EmergenciaRepository(BaseRepository[Emergencia, EmergenciaCreateSchema, EmergenciaUpdateSchema]):
    def __init__(self, db: AsyncSession):
        super().__init__(Emergencia, db)

    def _get_detalle_options(self):
        """Opciones de eager loading compartidas para traer todo el detalle de una emergencia."""
        return [
            selectinload(Emergencia.resumen_ia),
            selectinload(Emergencia.evidencias),
            selectinload(Emergencia.tecnicos_asignados).selectinload(Tecnico.especialidades),
            selectinload(Emergencia.historial).joinedload(HistorialEstado.estado),
            joinedload(Emergencia.vehiculo),
            selectinload(Emergencia.pago)
        ]

    async def get_detalle_by_id(self, emergencia_id: int) -> Optional[Emergencia]:
        stmt = (
            select(Emergencia)
            .options(*self._get_detalle_options())
            .where(Emergencia.id == emergencia_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_by_cliente(self, cliente_id: int) -> List[Emergencia]:
        stmt = (
            select(Emergencia)
            .options(*self._get_detalle_options())
            .where(Emergencia.idCliente == cliente_id)
            .order_by(desc(Emergencia.fecha), desc(Emergencia.hora))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_taller(self, taller_cod: str) -> List[Emergencia]:
        stmt = (
            select(Emergencia)
            .options(*self._get_detalle_options())
            .where(Emergencia.idTaller == taller_cod)
            .order_by(desc(Emergencia.fecha), desc(Emergencia.hora))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_disponibles_para_taller(
        self, especialidades_taller: List[int], estados_validos: List[int]
    ) -> List[Emergencia]:
        stmt = (
            select(Emergencia)
            .join(CategoriaProblema)
            .options(*self._get_detalle_options())
            .where(Emergencia.idTaller.is_(None))
            .where(Emergencia.idEstado.in_(estados_validos)) 
            .where(Emergencia.es_valida.is_(True))
            .where(CategoriaProblema.idEspecialidad.in_(especialidades_taller))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
