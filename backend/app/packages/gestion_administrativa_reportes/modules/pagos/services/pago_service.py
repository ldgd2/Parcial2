from sqlalchemy.ext.asyncio import AsyncSession
from app.packages.gestion_administrativa_reportes.modules.pagos.schemas.pago import PagoCreate

async def registrar_pago(data: PagoCreate, db: AsyncSession):
    pago = await Pago.create(db, obj_in=data.model_dump())
    await db.commit()
    return pago

async def obtener_pagos_emergencia(db: AsyncSession):
    return await Pago.get_all(db, )
