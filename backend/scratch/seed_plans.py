import asyncio
import os
import sys

# Agregar el directorio raíz de la aplicación al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import AsyncSessionLocal
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.suscripcion import PlanSuscripcion
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.permisos import Rol, Permiso
from app.db.base import *

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Seed Roles
        roles_data = ["ADMIN_TALLER", "MECANICO", "CLIENTE"]
        for role_name in roles_data:
            from sqlalchemy import select
            existing = (await session.execute(select(Rol).where(Rol.nombre == role_name))).scalar_one_or_none()
            if not existing:
                await Rol.create(session, obj_in={"nombre": role_name})

        # Seed Planes
        planes_data = [
            {"nombre": "Gratuita", "descripcion": "Plan básico gratuito", "precio_mensual": 0.0, "max_sucursales": 1, "max_tecnicos": 5, "max_admins_sucursal": 1},
            {"nombre": "Standar", "descripcion": "Plan estándar para negocios en crecimiento", "precio_mensual": 29.99, "max_sucursales": 3, "max_tecnicos": 15, "max_admins_sucursal": 2},
            {"nombre": "Profesional", "descripcion": "Plan para talleres profesionales con múltiples ubicaciones", "precio_mensual": 79.99, "max_sucursales": 10, "max_tecnicos": 50, "max_admins_sucursal": 5},
            {"nombre": "Deluxe", "descripcion": "Plan ilimitado para grandes corporaciones", "precio_mensual": 199.99, "max_sucursales": 9999, "max_tecnicos": 9999, "max_admins_sucursal": 9999},
        ]
        
        for plan in planes_data:
            from sqlalchemy import select
            existing = (await session.execute(select(PlanSuscripcion).where(PlanSuscripcion.nombre == plan["nombre"]))).scalar_one_or_none()
            if not existing:
                await PlanSuscripcion.create(session, obj_in=plan)

        await session.commit()
        print("Data seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
