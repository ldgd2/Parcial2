import asyncio
from app.db.session import AsyncSessionLocal
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado
from sqlalchemy import select

async def get_estados():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Estado))
        for r in res.scalars().all():
            print(f'Estado: {r.nombre}')

asyncio.run(get_estados())
