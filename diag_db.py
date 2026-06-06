import asyncio
import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico

async def check():
    async with AsyncSessionLocal() as db:
        talleres = (await db.execute(select(Taller))).scalars().all()
        print(f"Talleres: {len(talleres)}")
        for t in talleres:
            print(f" - {t.cod}: {t.nombre} ({t.latitud}, {t.longitud})")
            
        tecnicos = (await db.execute(select(Tecnico))).scalars().all()
        print(f"Tecnicos: {len(tecnicos)}")
        for t in tecnicos:
            print(f" - {t.correo} -> Taller: {t.idTaller}")

asyncio.run(check())
