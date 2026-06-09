import asyncio
import sys
import os

sys.path.append(r"c:\Users\ldgd2\OneDrive\Documentos\Proyectos_lider\taller\backend")

from app.db.session import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def run():
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as db:
        res = await db.execute(text("SELECT id, nombre FROM estado"))
        for r in res.fetchall():
            print(r)

asyncio.run(run())
