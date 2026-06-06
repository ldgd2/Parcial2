"""
Servicio de Autenticación — CU01
Valida credenciales de Cliente o Técnico y retorna un JWT.
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token
from app.packages.gestion_usuarios_seguridad.modules.auth.schemas.auth import LoginRequest, TokenResponse, RegisterAdminRequest
import random
import string
import re
from app.core.context import get_ip_context
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.usuario import Usuario
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.cliente import Cliente
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_administrativa_reportes.modules.reportes_kpis.models.bitacora import Bitacora
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from app.core.tenant_utils import get_tenant_schema_name
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.sucursal import Sucursal


def generate_workshop_code(name: str) -> str:
    """Generat a 10-char code based on name + 4 random chars."""
    # Clean name: only letters and numbers
    clean_name = re.sub(r'[^A-Z0-9]', '', name.upper())
    base = clean_name[:6]
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    # Ensure it's exactly 10 chars, padding with random if name too short
    code = base.ljust(6, 'X')[:6] + random_suffix
    return code


async def register_admin(data: RegisterAdminRequest, db: AsyncSession):
    """Registra un nuevo administrador y su taller."""
    try:

        # 1. Verificar si el correo ya existe en alguna tabla de usuarios
        if await Usuario.get_by_correo(db, data.correo):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo electrónico ya está registrado.",
            )

        # 2. Crear el Taller
        workshop_cod = generate_workshop_code(data.nombre_taller)
        taller_data = {
            "cod": workshop_cod,
            "nombre": data.nombre_taller,
            "direccion": data.direccion_taller,
            "latitud": data.latitud_taller,
            "longitud": data.longitud_taller,
            "estado": "ACTIVO",
            "plan_id": data.plan_id
        }
        taller = await Taller.create(db, obj_in=taller_data)

        # 3. Crear el Usuario Administrador
        usuario_data = {
            "nombre": data.nombre,
            "apellido": data.apellido,
            "correo": data.correo,
            "contrasena": hash_password(data.contrasena),
            "estado": "ACTIVO",
            "idTaller": taller.cod
        }
        usuario = await Usuario.create(db, obj_in=usuario_data)
        
        # Enlazar admin a taller
        await taller.update(db, obj_in={"id_admin": usuario.id})
        
        # Crear Sucursal Matriz
        sucursal_matriz = await Sucursal.create(db, obj_in={
            "id_taller": workshop_cod,
            "nombre": f"Matriz {data.nombre_taller}",
            "direccion": data.direccion_taller,
            "latitud": data.latitud_taller,
            "longitud": data.longitud_taller,
            "estado": "ACTIVO"
        })
        
        # Multitenancy: Crear el esquema
        schema_name = get_tenant_schema_name(data.nombre_taller, workshop_cod)
        try:
            await db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        except ProgrammingError:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Error creando el tenant")
        
        await db.commit()
        await db.refresh(usuario)
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"Error en register_admin: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        with open("error_log.txt", "a") as f:
            f.write(error_msg + "\n")
        raise HTTPException(status_code=500, detail=str(e))


async def login(data: LoginRequest, db: AsyncSession) -> TokenResponse:
    """Login para la aplicación móvil (Clientes y Técnicos)."""

    if data.rol == "cliente":
        user = await Cliente.get_by_correo(db, data.correo)
        if user is None or not verify_password(data.contrasena, user.contrasena):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )
        token = create_access_token(
            subject=user.id,
            extra_claims={"role": "cliente"},
        )

        # Registrar en bitácora
        await Bitacora.create(db, obj_in={
            "idUsuario": None,
            "accion": "LOGIN",
            "tabla": "cliente",
            "registro_id": str(user.id),
            "detalles": {"correo": user.correo, "rol": "cliente"},
            "ip": get_ip_context()
        })
        await db.commit()

        return TokenResponse(access_token=token, rol="cliente", user_id=user.id, nombre=user.nombre)

    elif data.rol == "tecnico":
        user = await Tecnico.get_by_correo(db, data.correo)
        if user is None or not verify_password(data.contrasena, user.contrasena):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )
        # Buscar nombre del taller
        workshop_name = None
        if user.idTaller:
            taller = await Taller.get_by_cod(db, user.idTaller)
            if taller:
                workshop_name = taller.nombre

        token = create_access_token(
            subject=user.id,
            extra_claims={"role": "tecnico", "taller": user.idTaller},
        )

        # Registrar en bitácora
        await Bitacora.create(db, obj_in={
            "idUsuario": None,  # No tenemos ID de usuario general aquí (es Cliente/Técnico)
            "accion": "LOGIN",
            "tabla": "tecnico",
            "registro_id": str(user.id),
            "detalles": {"correo": user.correo, "rol": "tecnico"},
            "ip": get_ip_context()
        })
        await db.commit()

        return TokenResponse(
            access_token=token, 
            rol="tecnico", 
            user_id=user.id,
            nombre=user.nombre, 
            cod_taller=user.idTaller,
            nombre_taller=workshop_name
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol inválido para login móvil. Use 'cliente' o 'tecnico'.",
        )


async def login_web(data: LoginRequest, db: AsyncSession) -> TokenResponse:
    """Login para la aplicación web (Administradores, Operadores, Supervisores)."""
    
    user = await Usuario.get_by_correo(db, data.correo)
    if user is None or not verify_password(data.contrasena, user.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
        
    # Obtener el nombre del rol desde la base de datos
    role_name = "admin" # fallback
    if getattr(user, 'id_rol', None):
        from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.permisos import Rol
        rol_obj = await db.get(Rol, user.id_rol)
        if rol_obj:
            # Mapeamos algunos nombres para mantener compatibilidad si es necesario
            role_name = rol_obj.nombre.lower()
            if role_name == "admin_taller":
                role_name = "admin"
            elif role_name == "super_admin":
                role_name = "admin" # temporal compat, depends requires 'admin' + GLOBAL check
                
    # Verificar acceso web
    # Todos menos cliente y mecanico/tecnico pueden acceder a la web (a menos que se especifique lo contrario)
    if role_name in ["cliente", "tecnico", "mecanico"]:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Este portal es solo para personal administrativo.",
        )
    
    token = create_access_token(
        subject=user.id,
        extra_claims={"role": role_name, "taller": user.idTaller, "sucursal": user.idSucursal},
    )

    # Registrar en bitácora
    await Bitacora.create(db, obj_in={
        "idUsuario": user.id,
        "accion": "LOGIN",
        "tabla": "usuario",
        "registro_id": str(user.id),
        "detalles": {"correo": user.correo, "rol": "admin"},
        "ip": get_ip_context()
    })
    await db.commit()

    # Buscar nombre del taller
    workshop_name = None
    if user.idTaller:
        taller = await Taller.get_by_cod(db, user.idTaller)
        if taller:
            workshop_name = taller.nombre

    return TokenResponse(
        access_token=token, 
        rol="admin", 
        user_id=user.id,
        nombre=user.nombre, 
        cod_taller=user.idTaller,
        nombre_taller=workshop_name,
        # TODO: si el frontend espera idSucursal en el response, podemos añadirlo al schema en el futuro.
    )

from sqlalchemy import select
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.permisos import Permiso, Rol, RolPermiso, PlanPermiso
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.suscripcion import PlanSuscripcion

async def get_me(current_user: dict, db: AsyncSession):
    user_id = current_user.get("user_id") or current_user.get("sub")
    taller_cod = current_user.get("taller") or current_user.get("idTaller")
    rol = current_user.get("role")
    
    usuario = await Usuario.get(db, int(user_id))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    taller = await Taller.get_by_cod(db, taller_cod) if taller_cod else None
    plan = None
    if taller and taller.plan_id:
        plan = await db.get(PlanSuscripcion, taller.plan_id)
        
    if getattr(usuario, 'id_rol', None):
        stmt_rol = select(Permiso.codigo).join(RolPermiso).where(RolPermiso.id_rol == usuario.id_rol)
    else:
        stmt_rol = select(Permiso.codigo).join(RolPermiso).join(Rol).where(Rol.nombre == "ADMIN_TALLER")
        
    result_rol = await db.execute(stmt_rol)
    permisos_rol = set(result_rol.scalars().all())
    
    permisos_plan = set()
    if taller and taller.plan_id:
        stmt_plan = select(Permiso.codigo).join(PlanPermiso).where(PlanPermiso.id_plan == taller.plan_id)
        result_plan = await db.execute(stmt_plan)
        permisos_plan = set(result_plan.scalars().all())
        
    permisos_finales = list(permisos_rol.intersection(permisos_plan)) if plan else list(permisos_rol) # fallback si no hay plan estricto
    
    return {
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "correo": usuario.correo
        },
        "taller": {
            "cod": taller.cod if taller else None,
            "nombre": taller.nombre if taller else None,
            "estado": taller.estado if taller else None
        },
        "plan": {
            "nombre": plan.nombre if plan else "Gratuito (Fallback)",
            "precio_mensual": float(plan.precio_mensual) if plan and plan.precio_mensual else 0.0,
            "max_sucursales": plan.max_sucursales if plan else 1,
            "max_tecnicos": plan.max_tecnicos if plan else 3
        },
        "sucursal": usuario.idSucursal,
        "permisos": permisos_finales
    }
