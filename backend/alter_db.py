import sys
import asyncio
from sqlalchemy import text
from app.db.session import engine

async def alter():
    async with engine.begin() as conn:
        await conn.execute(text('ALTER TABLE usuario ADD COLUMN IF NOT EXISTS id_rol INTEGER REFERENCES rol(id)'))
    print('ALTER completado')

if __name__ == '__main__':
    asyncio.run(alter())
