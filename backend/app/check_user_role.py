import asyncio
from app.db.session import SessionLocal
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.usuario import Usuario

async def check():
    async with SessionLocal() as db:
        users = await Usuario.get_all(db)
        for u in users:
            print(f"ID: {u.id}, Correo: {u.correo}, Rol ID: {u.id_rol}")

asyncio.run(check())
