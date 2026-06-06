import sys
import os
from pathlib import Path
from sqlalchemy import select

# Asegurar path
current_dir = Path(__file__).resolve().parent
backend_path = current_dir.parent.parent.parent.parent.parent / "backend"
backend_str = str(backend_path.absolute())

if backend_str not in sys.path:
    sys.path.insert(0, backend_str)

from app.db.session import AsyncSessionLocal
from app.db.base import (
    PlanSuscripcion, Rol, Permiso, Especialidad, Taller,
    Tecnico, Cliente, Vehiculo, Emergencia, Cotizacion, Estado, Prioridad
)

async def get_all_records(model):
    """Retorna todos los registros de un modelo."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(model))
        return result.scalars().all()

async def get_planes():
    return await get_all_records(PlanSuscripcion)

async def get_talleres():
    return await get_all_records(Taller)

async def get_clientes():
    return await get_all_records(Cliente)

async def get_tecnicos():
    return await get_all_records(Tecnico)

async def get_especialidades():
    return await get_all_records(Especialidad)

async def get_vehiculos():
    return await get_all_records(Vehiculo)
