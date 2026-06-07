import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def run():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text('SELECT id, "idEstado", "idCategoria", es_valida FROM emergencia ORDER BY id DESC LIMIT 5'))
        print("LAST EMERGENCIES:", res.all())

asyncio.run(run())
