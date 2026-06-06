import asyncio
import os
import sys
from pathlib import Path

# Configurar path para modulo app
current_dir = Path(__file__).resolve().parent
backend_path = current_dir.parent.parent.parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path.absolute()))

from sqlalchemy import select
from app.core.security import hash_password
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.usuario import Usuario
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.permisos import Rol
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.usuario_rol import UsuarioRol
from .db_utils import AsyncSessionLocal, get_planes

async def seed_saas():
    # Remove init_db
    
    async with AsyncSessionLocal() as session:
        # 1. Asegurar Plan Enterprise (o el mas alto)
        planes = await get_planes()
        plan_id = planes[-1].id if planes else None
        
        # 2. Asegurar Taller GLOBAL
        cod_global = "GLOBAL"
        existing_taller = (await session.execute(select(Taller).filter_by(cod=cod_global))).scalars().first()
        if not existing_taller:
            taller_global = Taller(
                cod=cod_global,
                nombre="SaaS Global Operations",
                direccion="Cloud",
                latitud=0.0,
                longitud=0.0,
                estado="ACTIVO",
                plan_id=plan_id
            )
            session.add(taller_global)
            await session.commit()
            print("✅ Taller GLOBAL creado.")
        else:
            print("✅ Taller GLOBAL ya existe.")
            
        # 3. Asegurar Rol SUPER_ADMIN
        existing_rol = (await session.execute(select(Rol).filter_by(nombre="SUPER_ADMIN"))).scalars().first()
        if not existing_rol:
            print("❌ El rol SUPER_ADMIN no existe. Por favor ejecuta 'python seeder.py' para actualizar planes y roles.")
            return

        # 4. Asegurar Usuario Super Admin
        correo_admin = "saas_admin@system.com"
        existing_admin = (await session.execute(select(Usuario).filter_by(correo=correo_admin))).scalars().first()
        if not existing_admin:
            admin_saas = Usuario(
                nombre="Super",
                apellido="Admin",
                correo=correo_admin,
                contrasena=hash_password("Admin123!"),
                estado="ACTIVO",
                idTaller=cod_global
            )
            session.add(admin_saas)
            await session.commit()
            print("✅ Usuario Super Admin (saas_admin@system.com) creado.")
            
            # Asignar rol
            user_rol = UsuarioRol(
                id_usuario=admin_saas.id,
                id_rol=existing_rol.id
            )
            session.add(user_rol)
            await session.commit()
            print("✅ Rol SUPER_ADMIN asignado.")
        else:
            print("✅ Usuario Super Admin ya existe.")

if __name__ == "__main__":
    asyncio.run(seed_saas())
