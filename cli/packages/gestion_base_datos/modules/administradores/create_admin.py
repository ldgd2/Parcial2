import asyncio
import os
import sys
from dotenv import load_dotenv

# Setup paths
backend_path = os.path.abspath(os.path.dirname(__file__))
if backend_path not in sys.path:
    sys.path.append(backend_path)

# Ir un nivel arriba para encontrar app si estamos en root o similar
root_path = os.path.abspath(os.path.join(backend_path, '..'))
if root_path not in sys.path:
    sys.path.append(root_path)

load_dotenv(os.path.join(root_path, ".env"))

from app.db.session import AsyncSessionLocal
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.usuario import Usuario
from app.core.security import hash_password
from sqlalchemy import select

async def create_admin():
    async with AsyncSessionLocal() as db:
        # Verificar si ya existe
        res = await db.execute(select(Usuario).where(Usuario.correo == "admin@demo.com"))
        if res.scalar_one_or_none():
            print("[INFO] Admin admin@demo.com ya existe.")
            return

        admin = Usuario(
            nombre="Admin",
            apellido="Demo",
            correo="admin@demo.com",
            contrasena=hash_password("admin123"),
            rol="admin",
            idTaller="TAL001",
            estado="ACTIVO"
        )
        db.add(admin)
        await db.commit()
        print("[OK] Administrador admin@demo.com creado con éxito (pass: admin123).")

if __name__ == "__main__":
    asyncio.run(create_admin())
