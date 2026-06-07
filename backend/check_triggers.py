import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def run():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT tgname, proname FROM pg_trigger t JOIN pg_proc p ON p.oid = t.tgfoid WHERE tgrelid = 'emergencia'::regclass;"))
        print(res.all())

asyncio.run(run())
