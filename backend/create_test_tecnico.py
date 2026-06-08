
import asyncio
import app.db.base
from app.db.session import AsyncSessionLocal
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.core.security import hash_password
from sqlalchemy import select

async def create_tecnico():
    async with AsyncSessionLocal() as db:
        # Check if taller exists
        taller = (await db.execute(select(Taller))).scalars().first()
        if not taller:
            print('No taller found, creating one...')
            taller = Taller(cod='TALTEST', nombre='Taller Test', direccion='...', estado='ACTIVO')
            db.add(taller)
            await db.commit()
            
        tecnico = await Tecnico.get_by_correo(db, 'tecnico@taller.com')
        if not tecnico:
            tecnico = Tecnico(
                nombre='Tecnico de Prueba',
                correo='tecnico@taller.com',
                contrasena=hash_password('admin123'),
                telefono='123456789',
                idTaller=taller.cod
            )
            db.add(tecnico)
            await db.commit()
            print('Tecnico created: tecnico@taller.com / admin123')
        else:
            tecnico.contrasena = hash_password('admin123')
            await db.commit()
            print('Tecnico already exists. Password reset to: admin123')

asyncio.run(create_tecnico())

