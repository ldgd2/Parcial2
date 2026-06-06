import asyncio
import bcrypt
import questionary
from sqlalchemy import select
from .db_utils import AsyncSessionLocal, Cliente

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

async def seed_nuevo_cliente():
    print("\n[+] Registro de Nuevo Cliente")
    nombre = await questionary.text("Nombre completo:").ask_async()
    correo = await questionary.text("Correo electrónico:").ask_async()
    contrasena = await questionary.password("Contraseña:").ask_async()
    
    if not nombre or not correo or not contrasena:
        return

    async with AsyncSessionLocal() as session:
        existing = (await session.execute(select(Cliente).filter_by(correo=correo))).scalars().first()
        if existing:
            print(f"❌ El correo {correo} ya está registrado.")
            return
            
        cliente = Cliente(
            nombre=nombre,
            correo=correo,
            contrasena=hash_password(contrasena)
        )
        session.add(cliente)
        await session.commit()
        print(f"\n✅ Cliente '{nombre}' ({correo}) creado exitosamente.")

if __name__ == "__main__":
    asyncio.run(seed_nuevo_cliente())
