from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.schemas.tecnico import TecnicoCreate, TecnicoUpdate
from app.core.security import hash_password
from sqlalchemy.exc import IntegrityError
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.repositories.tecnico_repo import TecnicoRepository

async def crear_tecnico(data: TecnicoCreate, db: AsyncSession) -> Tecnico:
    repo = TecnicoRepository(db)
    
    if await repo.get_by_correo(data.correo):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Técnico ya registrado con este correo.",
        )
    
    try:
        data.contrasena = hash_password(data.contrasena)
        tecnico = await repo.create(obj_in=data.model_dump())
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
    return await repo.get_with_especialidades(tecnico.id)

async def obtener_tecnico_by_id(tecnico_id: int, db: AsyncSession) -> Tecnico:
    repo = TecnicoRepository(db)
    return await repo.get_with_especialidades(tecnico_id)

async def obtener_tecnicos_taller(idTaller: str, db: AsyncSession):
    repo = TecnicoRepository(db)
    return await repo.get_by_taller_with_especialidades(idTaller)

async def actualizar_tecnico(tecnico_id: int, data: TecnicoUpdate, db: AsyncSession) -> Tecnico:
    repo = TecnicoRepository(db)
    tecnico = await repo.get(tecnico_id) # get from base repository
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    
    # We use a dict for partial updates because data.model_dump(exclude_unset=True) can be done
    update_data = data.model_dump(exclude_unset=True)
    if "contrasena" in update_data and update_data["contrasena"]:
        update_data["contrasena"] = hash_password(update_data["contrasena"])
        
    await repo.update(db_obj=tecnico, obj_in=update_data)
    await db.commit()
    return await repo.get_with_especialidades(tecnico_id)

async def desactivar_tecnico(tecnico_id: int, db: AsyncSession):
    repo = TecnicoRepository(db)
    tecnico = await repo.get(tecnico_id)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    
    tecnico = await repo.update(db_obj=tecnico, obj_in={"estado": "INACTIVO"})
    await db.commit()
    return tecnico


async def actualizar_especialidades_tecnico(tecnico_id: int, especialidades_ids: list, db: AsyncSession) -> Tecnico:
    """CU13 — Gestionar Rol: asigna/reemplaza especialidades del técnico."""
    repo = TecnicoRepository(db)
    tecnico = await repo.get(tecnico_id)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    
    await repo.update_especialidades(tecnico_id, especialidades_ids)
    await db.commit()
    return await repo.get_with_especialidades(tecnico_id)
