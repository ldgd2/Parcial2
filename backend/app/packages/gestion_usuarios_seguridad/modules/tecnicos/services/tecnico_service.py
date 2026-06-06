from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.schemas.tecnico import TecnicoCreate, TecnicoUpdate
from app.core.security import hash_password
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.suscripcion import PlanSuscripcion

async def crear_tecnico(data: TecnicoCreate, db: AsyncSession) -> Tecnico:
    
    # Validacion limite de suscripcion
    if data.idTaller:
        taller = await Taller.get_by_cod(db, data.idTaller)
        if taller and taller.plan_id:
            plan = await db.get(PlanSuscripcion, taller.plan_id)
            if plan:
                stmt_count = select(func.count(Tecnico.id)).where(Tecnico.idTaller == data.idTaller, Tecnico.estado == 'ACTIVO')
                count = (await db.execute(stmt_count)).scalar()
                if count >= plan.max_tecnicos:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Límite de técnicos ({plan.max_tecnicos}) alcanzado para el plan {plan.nombre}."
                    )

    if await Tecnico.get_by_correo(db, data.correo):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Técnico ya registrado con este correo.",
        )
    
    try:
        data.contrasena = hash_password(data.contrasena)
        tecnico = await Tecnico.create(db, obj_in=data.model_dump())
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fallo de integridad: El taller {data.idTaller} no existe o no tiene perfil activo."
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    # Re-recuperar con especialidades para serialización async
    return await Tecnico.get_with_especialidades(db, tecnico.id)

async def obtener_tecnico_by_id(tecnico_id: int, db: AsyncSession) -> Tecnico:
    return await Tecnico.get_with_especialidades(db, tecnico_id)

async def obtener_tecnicos_taller(idTaller: str, db: AsyncSession):
    return await Tecnico.get_by_taller_with_especialidades(db, idTaller)

async def actualizar_tecnico(tecnico_id: int, data: TecnicoUpdate, db: AsyncSession) -> Tecnico:
    tecnico = await Tecnico.get(db, tecnico_id) # get from base repository
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    
    # We use a dict for partial updates because data.model_dump(exclude_unset=True) can be done
    update_data = data.model_dump(exclude_unset=True)
    if "contrasena" in update_data and update_data["contrasena"]:
        update_data["contrasena"] = hash_password(update_data["contrasena"])
        
    await tecnico.update(db, obj_in=update_data)
    await db.commit()
    return await Tecnico.get_with_especialidades(db, tecnico_id)

async def desactivar_tecnico(tecnico_id: int, db: AsyncSession):
    tecnico = await Tecnico.get(db, tecnico_id)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    
    tecnico = await tecnico.update(db, obj_in={"estado": "INACTIVO"})
    await db.commit()
    return tecnico


async def actualizar_especialidades_tecnico(tecnico_id: int, especialidades_ids: list, db: AsyncSession) -> Tecnico:
    """CU13 — Gestionar Rol: asigna/reemplaza especialidades del técnico."""
    tecnico = await Tecnico.get(db, tecnico_id)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    
    await Tecnico.update_especialidades(db, tecnico_id, especialidades_ids)
    await db.commit()
    return await Tecnico.get_with_especialidades(db, tecnico_id)
