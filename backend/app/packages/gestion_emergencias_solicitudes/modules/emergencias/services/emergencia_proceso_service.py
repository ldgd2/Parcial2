from sqlalchemy.ext.asyncio import AsyncSession
from app.packages.gestion_administrativa_reportes.modules.pagos.schemas.transacciones import EvidenciaCreate, HistorialEstadoCreate
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.evidencia_repo import EvidenciaRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.historial_repo import HistorialEstadoRepository
from sqlalchemy import select
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.historial_estado import HistorialEstado
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.evidencia import Evidencia

async def registrar_evidencia(data: EvidenciaCreate, db: AsyncSession):
    repo = EvidenciaRepository(db)
    evidencia = await repo.create(obj_in=data.model_dump())
    await db.commit()
    return evidencia

async def registrar_cambio_estado(data: HistorialEstadoCreate, db: AsyncSession):
    repo = HistorialEstadoRepository(db)
    historial = await repo.create(obj_in=data.model_dump())
    await db.commit()
    return historial

async def obtener_historial_emergencia(idEmergencia: int, db: AsyncSession):
    result = await db.execute(select(HistorialEstado).where(HistorialEstado.idEmergencia == idEmergencia))
    return result.scalars().all()

async def obtener_evidencias_emergencia(idEmergencia: int, db: AsyncSession):
    result = await db.execute(select(Evidencia).where(Evidencia.idEmergencia == idEmergencia))
    return result.scalars().all()
