import sys
from pathlib import Path
import asyncio

current_dir = Path(__file__).resolve().parent
backend_path = current_dir / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT cod, latitud, longitud FROM public.taller WHERE cod = 'GERLEXSRYK'"))
        taller = res.fetchone()
        if taller:
            print(f"Taller coords: {taller.latitud}, {taller.longitud}")
        
        res_s = await db.execute(text("SELECT id, latitud, longitud FROM public.sucursal WHERE id_taller = 'GERLEXSRYK'"))
        sucursales = res_s.fetchall()
        for s in sucursales:
            print(f"Sucursal {s.id} coords: {s.latitud}, {s.longitud}")
            
        res_e = await db.execute(text("SELECT id, latitud, longitud FROM public.emergencia WHERE id = 18"))
        e = res_e.fetchone()
        if e:
            print(f"Emergencia coords: {e.latitud}, {e.longitud}")

asyncio.run(check())
