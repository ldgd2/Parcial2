import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from app.db.base import * # load all models
from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.suscripcion import PlanSuscripcion
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.permisos import Permiso, PlanPermiso

async def run():
    async with AsyncSessionLocal() as session:
        planes = (await session.execute(select(PlanSuscripcion))).scalars().all()
        permisos = (await session.execute(select(Permiso).where(Permiso.codigo != 'PERMISO_GESTIONAR_SAAS'))).scalars().all()
        
        for plan in planes:
            for permiso in permisos:
                # check if exists
                exists = (await session.execute(select(PlanPermiso).where(PlanPermiso.id_plan == plan.id, PlanPermiso.id_permiso == permiso.id))).scalar_one_or_none()
                if not exists:
                    pp = PlanPermiso(id_plan=plan.id, id_permiso=permiso.id)
                    session.add(pp)
        await session.commit()
        print("Permissions for plans fixed!")

asyncio.run(run())
