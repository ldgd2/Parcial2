import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.base import Usuario, Rol, Taller  # This loads all models into the registry
from app.core.security import hash_password

import questionary
from rich.console import Console

console = Console()

async def create_super_admin(email: str, password: str):
    async with AsyncSessionLocal() as db:
        # Check if role SUPER_ADMIN exists
        result = await db.execute(select(Rol).where(Rol.nombre == "SUPER_ADMIN"))
        rol = result.scalars().first()
        if not rol:
            console.print("[bold red]Error: Rol SUPER_ADMIN no encontrado. Asegurate de correr el seeder básico antes.[/bold red]")
            return

        # Check if email exists
        result = await db.execute(select(Usuario).where(Usuario.correo == email))
        user = result.scalars().first()
        
        if user:
            console.print(f"[bold yellow]Atención: El usuario {email} ya existe. Actualizando contraseña y rol...[/bold yellow]")
            user.contrasena = hash_password(password)
            user.id_rol = rol.id
            user.idTaller = None
        else:
            console.print(f"[bold green]Creando nuevo usuario root: {email}...[/bold green]")
            user = Usuario(
                nombre="Super",
                apellido="Admin",
                correo=email,
                contrasena=hash_password(password),
                id_rol=rol.id,
                estado="ACTIVO",
                idTaller=None
            )
            db.add(user)
        
        await db.commit()
        console.print("[bold green]¡Super Administrador configurado con éxito![/bold green]")

def run_seed_root():
    console.print("\n[bold cyan]=== CREACIÓN DE SUPER ADMINISTRADOR ROOT ===[/bold cyan]\n")
    email = questionary.text("Correo electrónico del Root:", default="root@sys.com").ask()
    password = questionary.password("Contraseña del Root:").ask()
    
    if not email or not password:
        console.print("[bold red]Operación cancelada. El correo y la contraseña son obligatorios.[/bold red]")
        return
        
    asyncio.run(create_super_admin(email, password))

if __name__ == "__main__":
    run_seed_root()
