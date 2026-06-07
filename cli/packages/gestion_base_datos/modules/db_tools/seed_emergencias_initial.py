import asyncio
import os
import sys

# Execution from CLI sets PYTHONPATH correctly

# Esto fuerza a SQLAlchemy a cargar el registry completo de todos los modelos
import app.db.base 

from app.db.session import AsyncSessionLocal
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.prioridad import Prioridad
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.categoria_problema import CategoriaProblema
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.suscripcion import PlanSuscripcion
from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.permisos import Rol

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Seed Roles (del seed_plans anterior)
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

        # Seed Estados Emergencias
        estados_data = [
            {"id": 1, "nombre": "PENDIENTE", "descripcion": "Emergencia reportada, sin taller asignado"},
            {"id": 2, "nombre": "ASIGNADO", "descripcion": "Taller asignado"},
            {"id": 3, "nombre": "INICIADA", "descripcion": "Reparación iniciada"},
            {"id": 4, "nombre": "CANCELADA", "descripcion": "Emergencia cancelada"},
            {"id": 5, "nombre": "EN_CAMINO", "descripcion": "Técnico en camino"},
            {"id": 6, "nombre": "ATENDIDO", "descripcion": "Servicio finalizado"},
        ]
        for estado in estados_data:
            from sqlalchemy import select
            existing = (await session.execute(select(Estado).where(Estado.id == estado["id"]))).scalar_one_or_none()
            if not existing:
                await Estado.create(session, obj_in=estado)

        # Seed Prioridades
        prioridades_data = [
            {"id": 1, "descripcion": "BAJA", "nivel": 1},
            {"id": 2, "descripcion": "MEDIA", "nivel": 2},
            {"id": 3, "descripcion": "ALTA", "nivel": 3},
            {"id": 4, "descripcion": "CRÍTICA", "nivel": 4},
        ]
        for prioridad in prioridades_data:
            from sqlalchemy import select
            existing = (await session.execute(select(Prioridad).where(Prioridad.id == prioridad["id"]))).scalar_one_or_none()
            if not existing:
                try:
                    await Prioridad.create(session, obj_in=prioridad)
                except Exception:
                    await Prioridad.create(session, obj_in={"id": prioridad["id"], "descripcion": prioridad["descripcion"]})


        # Seed Categorias Problema
        categorias_data = [
            {"id": 1, "descripcion": "Problema de Motor"},
            {"id": 2, "descripcion": "Neumáticos"},
            {"id": 3, "descripcion": "Batería"},
            {"id": 4, "descripcion": "Frenos"},
            {"id": 5, "descripcion": "OTROS"},
        ]
        for categoria in categorias_data:
            from sqlalchemy import select
            existing = (await session.execute(select(CategoriaProblema).where(CategoriaProblema.id == categoria["id"]))).scalar_one_or_none()
            if not existing:
                try:
                    await CategoriaProblema.create(session, obj_in=categoria)
                except Exception:
                    await CategoriaProblema.create(session, obj_in={"id": categoria["id"], "descripcion": categoria["descripcion"]})

        await session.commit()
        print("Seed Initial Data completado satisfactoriamente (Estados, Roles, Planes, Prioridades, Categorías)")

if __name__ == "__main__":
    asyncio.run(seed_data())
