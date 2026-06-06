import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def run():
    async with AsyncSessionLocal() as session:
        await session.execute(text('UPDATE public.usuario SET "idTaller" = NULL WHERE "idTaller" = \'ROOT\''))
        await session.execute(text('DELETE FROM public.emergencia WHERE "idTaller" = \'ROOT\''))
        await session.execute(text('DELETE FROM public.taller WHERE cod = \'ROOT\''))
        await session.commit()

asyncio.run(run())
