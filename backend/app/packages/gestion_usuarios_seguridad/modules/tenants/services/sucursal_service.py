from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.sucursal import Sucursal
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.suscripcion import PlanSuscripcion
from app.packages.gestion_usuarios_seguridad.modules.tenants.schemas.sucursal_schema import SucursalCreate, SucursalUpdate, SucursalAdminCreate

async def crear_sucursal(data: SucursalCreate, db: AsyncSession) -> Sucursal:
    taller = await Taller.get_by_cod(db, data.id_taller)
    if not taller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Taller no encontrado."
        )

    # Validacion limite de suscripcion
    if taller.plan_id:
        plan = await db.get(PlanSuscripcion, taller.plan_id)
        if plan:
            stmt_count = select(func.count(Sucursal.id)).where(Sucursal.id_taller == data.id_taller, Sucursal.estado == 'ACTIVO')
            count = (await db.execute(stmt_count)).scalar()
            if count >= plan.max_sucursales:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Límite de sucursales ({plan.max_sucursales}) alcanzado para el plan {plan.nombre}."
                )

    try:
        sucursal = await Sucursal.create(db, obj_in=data.model_dump())
        await db.commit()
        return sucursal
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def obtener_sucursal(sucursal_id: int, db: AsyncSession) -> Sucursal:
    sucursal = await Sucursal.get(db, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada.")
    return sucursal

async def obtener_sucursales_taller(id_taller: str, db: AsyncSession):
    stmt = select(Sucursal).where(Sucursal.id_taller == id_taller)
    result = await db.execute(stmt)
    return result.scalars().all()

async def actualizar_sucursal(sucursal_id: int, data: SucursalUpdate, db: AsyncSession) -> Sucursal:
    sucursal = await Sucursal.get(db, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada.")
    
    await sucursal.update(db, obj_in=data.model_dump(exclude_unset=True))
    await db.commit()
    return sucursal

async def desactivar_sucursal(sucursal_id: int, db: AsyncSession):
    sucursal = await Sucursal.get(db, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada.")
    
    await sucursal.update(db, obj_in={"estado": "INACTIVO"})
    await db.commit()
    return sucursal

from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.usuario import Usuario
from app.core.security import hash_password

async def crear_admin_sucursal(sucursal_id: int, data: SucursalAdminCreate, db: AsyncSession):
    sucursal = await Sucursal.get(db, sucursal_id)
    if not sucursal or sucursal.id_taller != data.id_taller:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada o no pertenece al taller.")

    # Validacion limite de suscripcion
    taller = await Taller.get_by_cod(db, data.id_taller)
    if taller and taller.plan_id:
        plan = await db.get(PlanSuscripcion, taller.plan_id)
        if plan:
            stmt_count = select(func.count(Usuario.id)).where(Usuario.idSucursal == sucursal_id, Usuario.estado == 'ACTIVO')
            count = (await db.execute(stmt_count)).scalar()
            if count >= plan.max_admins_sucursal:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Límite de admins ({plan.max_admins_sucursal}) alcanzado para esta sucursal según el plan {plan.nombre}."
                )

    if await Usuario.get_by_correo(db, data.correo):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Correo ya registrado.")

    try:
        nuevo_usuario = Usuario(
            nombre=data.nombre,
            apellido=data.apellido,
            correo=data.correo,
            contrasena=hash_password(data.contrasena),
            idTaller=data.id_taller,
            idSucursal=sucursal_id
        )
        db.add(nuevo_usuario)
        await db.commit()
        await db.refresh(nuevo_usuario)
        
        # Asignar rol ADMIN_SUCURSAL
        from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.permisos import Rol
        stmt_rol = select(Rol).where(Rol.nombre == "ADMIN_SUCURSAL")
        rol = (await db.execute(stmt_rol)).scalar_one_or_none()
        if rol:
            nuevo_usuario.id_rol = rol.id
            await db.commit()

        return nuevo_usuario
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def obtener_candidatos_admin_taller(id_taller: str, db: AsyncSession):
    # Obtener todos los usuarios del taller
    stmt = select(Usuario).where(Usuario.idTaller == id_taller, Usuario.estado == 'ACTIVO')
    result = await db.execute(stmt)
    return result.scalars().all()

async def asignar_admin_existente(sucursal_id: int, usuario_id: int, db: AsyncSession):
    sucursal = await Sucursal.get(db, sucursal_id)
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada.")
        
    usuario = await db.get(Usuario, usuario_id)
    if not usuario or usuario.idTaller != sucursal.id_taller:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o no pertenece a este taller.")
        
    usuario.idSucursal = sucursal_id
    
    # Asignar el rol ADMIN_SUCURSAL si no es SUPER_ADMIN o ADMIN_TALLER
    from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.permisos import Rol
    stmt_rol = select(Rol).where(Rol.nombre == "ADMIN_SUCURSAL")
    rol = (await db.execute(stmt_rol)).scalar_one_or_none()
    
    if rol:
        usuario.id_rol = rol.id

    await db.commit()
    await db.refresh(usuario)
    return usuario
