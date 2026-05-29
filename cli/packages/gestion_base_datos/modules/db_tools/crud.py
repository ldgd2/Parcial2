import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.core.security import hash_password
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.cliente import Cliente
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico

async def desactivar_taller(cod: str):
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Taller).where(Taller.cod == cod))
        taller = res.scalar_one_or_none()
        if not taller:
            print(f"Error: No se encontró el taller con COD {cod}")
            return
        taller.estado = "INACTIVO"
        await db.commit()
        print(f"[OK] Taller {taller.nombre} DESACTIVADO.")

async def desactivar_cliente(correo: str):
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Cliente).where(Cliente.correo == correo))
        cliente = res.scalar_one_or_none()
        if not cliente:
            print(f"Error: No se encontró el cliente con correo {correo}")
            return
        cliente.estado = "INACTIVO"
        await db.commit()
        print(f"[OK] Cliente {cliente.nombre} DESACTIVADO.")
