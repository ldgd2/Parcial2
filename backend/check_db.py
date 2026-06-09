import asyncio
import sys
sys.path.append('.')
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_emergencias_solicitudes.modules.auxilio_solicitudes.models.asignacion_tecnico_emergencia import AsignacionTecnicoEmergencia

engine = create_async_engine('postgresql+asyncpg://postgres:postgres@localhost/parcial2')
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def main():
    async with SessionLocal() as db:
        e = await db.get(Emergencia, 7)
        if e:
            print(f'Emergencia {e.id}: idTaller={e.idTaller}, idEstado={e.idEstado}')
            asign = await db.execute(select(AsignacionTecnicoEmergencia).where(AsignacionTecnicoEmergencia.idEmergencia == 7))
            for a in asign.scalars():
                print(f'Asignacion: idTecnico={a.idTecnico}')
        else:
            print("Emergencia 7 no existe")

asyncio.run(main())
