import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

import asyncio
import app.db.base
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT * FROM public.alembic_version"))
        print("PUBLIC ALEMBIC:", res.all())
        
        try:
            res = await db.execute(text("SELECT count(*) FROM public.bitacora"))
            print("PUBLIC BITACORA COUNT:", res.all())
        except Exception as e:
            print("PUBLIC BITACORA ERROR:", e)
            await db.rollback()
        
        # Check schemas
        schemas = await db.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'public') AND schema_name NOT LIKE 'pg_%'"))
        for s in schemas.scalars().all():
            try:
                res = await db.execute(text(f"SELECT * FROM {s}.alembic_version"))
                print(f"{s}:", res.all())
            except Exception as e:
                print(f"{s} missing. Creating and stamping...")
                await db.rollback()
                await db.execute(text(f"CREATE TABLE {s}.alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))"))
                await db.execute(text(f"INSERT INTO {s}.alembic_version (version_num) VALUES ('32242c242eb2')"))
                await db.commit()
                print(f"{s} stamped successfully.")

if __name__ == "__main__":
    asyncio.run(check())
