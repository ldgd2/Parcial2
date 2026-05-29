from sqlalchemy.ext.asyncio import AsyncSession
from app.packages.gestion_administrativa_reportes.modules.pagos.schemas.pago import PagoCreate
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.pago_repo import PagoRepository

async def registrar_pago(data: PagoCreate, db: AsyncSession):
    repo = PagoRepository(db)
    pago = await repo.create(obj_in=data.model_dump())
    await db.commit()
    return pago

async def obtener_pagos_emergencia(db: AsyncSession):
    repo = PagoRepository(db)
    return await repo.get_all()
