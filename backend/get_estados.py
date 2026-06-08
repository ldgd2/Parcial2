import asyncio
from app.db.session import AsyncSessionLocal
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Estado))
        estados = result.scalars().all()
        for e in estados:
            print(f'{e.id}: {e.nombre}')

if __name__ == '__main__':
    asyncio.run(main())
