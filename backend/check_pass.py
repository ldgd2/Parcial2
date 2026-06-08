
import asyncio
import app.db.base
from app.db.session import AsyncSessionLocal
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Tecnico))
        for t in res.scalars().all():
            print(f'Correo: {t.correo}, PassHash: {t.contrasena[:10]}...')

asyncio.run(check())

