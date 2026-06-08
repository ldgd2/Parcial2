
import asyncio
import app.db.base
from app.db.session import AsyncSessionLocal
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.models.tecnico import Tecnico
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.schemas.tecnico import TecnicoCreate
from app.packages.gestion_usuarios_seguridad.modules.tecnicos.services.tecnico_service import crear_tecnico
from app.core.security import verify_password
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        # Create a user mimicking the endpoint
        data = TecnicoCreate(
            nombre='Pepe Prueba',
            correo='pepe.prueba2@test.com',
            telefono='555555',
            idTaller='GERLEXFOAH',
            contrasena='pepe123'
        )
        try:
            tecnico = await crear_tecnico(data, db)
            print(f'Creado. Hash devuelto en objecto: {tecnico.contrasena[:15]}...')
        except Exception as e:
            print(f'Error creating: {e}')
        
        # Now fetch from DB to make sure the hash was saved
        tecnico_db = await Tecnico.get_by_correo(db, 'pepe.prueba2@test.com')
        if not tecnico_db:
            print('Not found in DB!')
            return
            
        print(f'Pass in DB: {tecnico_db.contrasena[:15]}...')
        
        # Verify
        is_valid = verify_password('pepe123', tecnico_db.contrasena)
        print(f'Verify pepe123: {is_valid}')

asyncio.run(check())

