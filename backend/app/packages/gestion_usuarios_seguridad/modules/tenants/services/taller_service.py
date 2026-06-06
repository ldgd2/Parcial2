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


def generate_workshop_code(name: str) -> str:
    """Genera un código de 10 caracteres basado en el nombre + 4 caracteres aleatorios."""
    clean_name = re.sub(r'[^A-Z0-9]', '', name.upper())
    base = clean_name[:6]
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    code = base.ljust(6, 'X')[:6] + random_suffix
    return code


async def obtener_taller_por_codigo(cod: str, db: AsyncSession) -> Taller:
    taller = await Taller.get_with_especialidades(db, cod)
    if taller:
        taller.especialidades = [a.especialidad for a in taller.asignaciones]
    if taller is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Taller no encontrado.",
        )
    return taller


async def actualizar_especialidades_taller(cod: str, especialidades_ids: list[int], db: AsyncSession):
    taller = await obtener_taller_por_codigo(cod, db)
    await Taller.update_especialidades(db, cod, especialidades_ids)
    await db.commit()
    return await obtener_taller_por_codigo(cod, db)


from app.core.tenant_utils import get_tenant_schema_name
from sqlalchemy import text, select
from sqlalchemy.exc import ProgrammingError
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.suscripcion import PlanSuscripcion
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.sucursal import Sucursal

async def crear_taller(data: TallerCreate, admin_id: int, db: AsyncSession) -> Taller:
    workshop_cod = generate_workshop_code(data.nombre)
    
    # Buscar plan Gratuito por defecto
    plan_gratuito = (await db.execute(select(PlanSuscripcion).where(PlanSuscripcion.nombre == "Gratuita"))).scalar_one_or_none()
    plan_id = plan_gratuito.id if plan_gratuito else None
    
    taller_data = {
        "cod": workshop_cod,
        "nombre": data.nombre,
        "direccion": data.direccion,
        "estado": "ACTIVO",
        "id_admin": admin_id,
        "plan_id": plan_id
    }
    taller = await Taller.create(db, obj_in=taller_data)
    
    # Crear Sucursal Matriz
    sucursal_matriz = await Sucursal.create(db, obj_in={
        "id_taller": workshop_cod,
        "nombre": f"Matriz {data.nombre}",
        "direccion": data.direccion,
        "latitud": data.latitud,
        "longitud": data.longitud,
        "estado": "ACTIVO"
    })
    
    # Multitenancy: Crear el esquema
    schema_name = get_tenant_schema_name(data.nombre, workshop_cod)
    try:
        await db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        
        await db.commit() # Commit schema, taller and sucursal
        
    except ProgrammingError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error creando el tenant")
        
    return taller


async def listar_talleres_admin(admin_id: int, db: AsyncSession):
    talleres = await Taller.get_by_admin_with_especialidades(db, admin_id)
    # Transformar para el schema
    for t in talleres:
        t.especialidades = [a.especialidad for a in t.asignaciones]
    return talleres


async def actualizar_taller(cod: str, data: TallerUpdate, db: AsyncSession) -> Taller:
    taller = await obtener_taller_por_codigo(cod, db)
    
    update_data = data.model_dump(exclude_unset=True)
    # Exclude especialidades from direct update as they are handled differently
    update_data.pop("especialidades", None)
    
    await taller.update(db, obj_in=update_data)
    
    # Sincronizar especialidades
    if data.especialidades is not None:
        await Taller.update_especialidades(db, cod, data.especialidades)
    
    await db.commit()
    return await obtener_taller_por_codigo(cod, db)


async def actualizar_disponibilidad(
    cod: str,
    data: DisponibilidadUpdate,
    db: AsyncSession,
) -> TallerOut:
    """CU06 — El taller actualiza su estado operativo."""
    taller = await obtener_taller_por_codigo(cod, db)
    if data.estado not in ("ACTIVO", "INACTIVO"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado debe ser 'ACTIVO' o 'INACTIVO'.",
        )
    
    taller = await taller.update(db, obj_in={"estado": data.estado})
    await db.commit()
    return TallerOut(
        cod=taller.cod,
        nombre=taller.nombre,
        direccion=taller.direccion,
        estado=taller.estado,
    )


async def listar_talleres_activos(db: AsyncSession):
    return await Taller.get_activos(db, )
