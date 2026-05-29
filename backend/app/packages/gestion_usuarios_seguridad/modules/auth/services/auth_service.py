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

from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.repositories.usuario_repo import UsuarioRepository
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.repositories.cliente_repo import ClienteRepository
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.repositories.tecnico_repo import TecnicoRepository
from app.packages.gestion_usuarios_seguridad.modules.tenants.repositories.taller_repo import TallerRepository
from app.packages.gestion_administrativa_reportes.modules.reportes_kpis.repositories.bitacora_repo import BitacoraRepository

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
        usuario_repo = UsuarioRepository(db)
        taller_repo = TallerRepository(db)

        # 1. Verificar si el correo ya existe en alguna tabla de usuarios
        if await usuario_repo.get_by_correo(data.correo):
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
            "estado": "ACTIVO"
        }
        taller = await taller_repo.create(obj_in=taller_data)

        # 3. Crear el Usuario Administrador
        usuario_data = {
            "nombre": data.nombre,
            "apellido": data.apellido,
            "correo": data.correo,
            "contrasena": hash_password(data.contrasena),
            "estado": "ACTIVO",
            "idTaller": taller.cod
        }
        usuario = await usuario_repo.create(obj_in=usuario_data)
        
        # Enlazar admin a taller
        await taller_repo.update(db_obj=taller, obj_in={"id_admin": usuario.id})
        
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
    bitacora_repo = BitacoraRepository(db)

    if data.rol == "cliente":
        cliente_repo = ClienteRepository(db)
        user = await cliente_repo.get_by_correo(data.correo)
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
        await bitacora_repo.create(obj_in={
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
        tecnico_repo = TecnicoRepository(db)
        taller_repo = TallerRepository(db)
        user = await tecnico_repo.get_by_correo(data.correo)
        if user is None or not verify_password(data.contrasena, user.contrasena):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )
        # Buscar nombre del taller
        workshop_name = None
        if user.idTaller:
            taller = await taller_repo.get_by_cod(user.idTaller)
            if taller:
                workshop_name = taller.nombre

        token = create_access_token(
            subject=user.id,
            extra_claims={"role": "tecnico", "taller": user.idTaller},
        )

        # Registrar en bitácora
        await bitacora_repo.create(obj_in={
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
    """Login para la aplicación web (Administradores de Taller)."""
    if data.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Este portal es solo para administradores.",
        )

    usuario_repo = UsuarioRepository(db)
    taller_repo = TallerRepository(db)
    bitacora_repo = BitacoraRepository(db)

    user = await usuario_repo.get_by_correo(data.correo)
    if user is None or not verify_password(data.contrasena, user.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    
    token = create_access_token(
        subject=user.id,
        extra_claims={"role": "admin", "taller": user.idTaller},
    )

    # Registrar en bitácora
    await bitacora_repo.create(obj_in={
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
        taller = await taller_repo.get_by_cod(user.idTaller)
        if taller:
            workshop_name = taller.nombre

    return TokenResponse(
        access_token=token, 
        rol="admin", 
        user_id=user.id,
        nombre=user.nombre, 
        cod_taller=user.idTaller,
        nombre_taller=workshop_name
    )
