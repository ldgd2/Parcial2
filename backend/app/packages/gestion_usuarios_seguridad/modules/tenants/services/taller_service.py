"""
Servicio de Talleres — CU06 (Disponibilidad)
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_usuarios_seguridad.modules.tenants.schemas.taller import DisponibilidadUpdate, TallerOut, TallerCreate, TallerUpdate
import re
import random
import string
from app.packages.gestion_usuarios_seguridad.modules.tenants.repositories.taller_repo import TallerRepository


def generate_workshop_code(name: str) -> str:
    """Genera un código de 10 caracteres basado en el nombre + 4 caracteres aleatorios."""
    clean_name = re.sub(r'[^A-Z0-9]', '', name.upper())
    base = clean_name[:6]
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    code = base.ljust(6, 'X')[:6] + random_suffix
    return code


async def obtener_taller_por_codigo(cod: str, db: AsyncSession) -> Taller:
    repo = TallerRepository(db)
    taller = await repo.get_with_especialidades(cod)
    if taller:
        taller.especialidades = [a.especialidad for a in taller.asignaciones]
    if taller is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Taller no encontrado.",
        )
    return taller


async def actualizar_especialidades_taller(cod: str, especialidades_ids: List[int], db: AsyncSession):
    repo = TallerRepository(db)
    taller = await obtener_taller_por_codigo(cod, db)
    await repo.update_especialidades(cod, especialidades_ids)
    await db.commit()
    return await obtener_taller_por_codigo(cod, db)


async def crear_taller(data: TallerCreate, admin_id: int, db: AsyncSession) -> Taller:
    repo = TallerRepository(db)
    workshop_cod = generate_workshop_code(data.nombre)
    taller_data = {
        "cod": workshop_cod,
        "nombre": data.nombre,
        "direccion": data.direccion,
        "latitud": data.latitud,
        "longitud": data.longitud,
        "estado": "ACTIVO",
        "id_admin": admin_id
    }
    taller = await repo.create(obj_in=taller_data)
    await db.commit()
    return taller


async def listar_talleres_admin(admin_id: int, db: AsyncSession):
    repo = TallerRepository(db)
    talleres = await repo.get_by_admin_with_especialidades(admin_id)
    # Transformar para el schema
    for t in talleres:
        t.especialidades = [a.especialidad for a in t.asignaciones]
    return talleres


async def actualizar_taller(cod: str, data: TallerUpdate, db: AsyncSession) -> Taller:
    repo = TallerRepository(db)
    taller = await obtener_taller_por_codigo(cod, db)
    
    update_data = data.model_dump(exclude_unset=True)
    # Exclude especialidades from direct update as they are handled differently
    update_data.pop("especialidades", None)
    
    await repo.update(db_obj=taller, obj_in=update_data)
    
    # Sincronizar especialidades
    if data.especialidades is not None:
        await repo.update_especialidades(cod, data.especialidades)
    
    await db.commit()
    return await obtener_taller_por_codigo(cod, db)


async def actualizar_disponibilidad(
    cod: str,
    data: DisponibilidadUpdate,
    db: AsyncSession,
) -> TallerOut:
    """CU06 — El taller actualiza su estado operativo."""
    repo = TallerRepository(db)
    taller = await obtener_taller_por_codigo(cod, db)
    if data.estado not in ("ACTIVO", "INACTIVO"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado debe ser 'ACTIVO' o 'INACTIVO'.",
        )
    
    taller = await repo.update(db_obj=taller, obj_in={"estado": data.estado})
    await db.commit()
    return TallerOut(
        cod=taller.cod,
        nombre=taller.nombre,
        direccion=taller.direccion,
        estado=taller.estado,
    )


async def listar_talleres_activos(db: AsyncSession):
    repo = TallerRepository(db)
    return await repo.get_activos()
