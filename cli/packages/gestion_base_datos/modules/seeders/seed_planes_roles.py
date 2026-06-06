import asyncio
from sqlalchemy import select
from .db_utils import AsyncSessionLocal, PlanSuscripcion, Rol, Permiso
# Necesitamos RolPermiso para la relación
import sys
from pathlib import Path
current_dir = Path(__file__).resolve().parent
backend_path = current_dir.parent.parent.parent.parent.parent / "backend"
backend_str = str(backend_path.absolute())
if backend_str not in sys.path:
    sys.path.insert(0, backend_str)

from app.packages.gestion_usuarios_seguridad.modules.suscripciones_roles.models.permisos import RolPermiso, PlanPermiso

async def seed_planes_y_roles():
    async with AsyncSessionLocal() as session:
        print("\n[+] Sembrando Permisos del Sistema...")
        permisos_data = [
            ("PERMISO_VER_DASHBOARD", "Acceso al tablero principal"),
            ("PERMISO_VER_REPORTES", "Acceso a reportes y métricas"),
            ("PERMISO_VER_TECNICO", "Ver lista de técnicos"),
            ("PERMISO_GESTIONAR_TECNICO", "Crear, editar o desactivar técnicos"),
            ("PERMISO_VER_SUCURSALES", "Ver lista de sucursales"),
            ("PERMISO_GESTIONAR_SUCURSALES", "Crear o editar sucursales"),
            ("PERMISO_VER_TRABAJOS", "Ver lista de trabajos y emergencias"),
            ("PERMISO_GESTIONAR_TRABAJOS", "Asignar trabajos, cambiar estados"),
            ("PERMISO_GESTIONAR_SAAS", "Gestionar talleres SaaS (Solo Super Admin)")
        ]
        
        for cod, desc in permisos_data:
            existing = (await session.execute(select(Permiso).where(Permiso.codigo == cod))).scalar_one_or_none()
            if not existing:
                await Permiso.create(session, obj_in={"codigo": cod, "descripcion": desc})
                print(f"  - Creado permiso: {cod}")

        # Guardar permisos para usarlos luego
        permisos_db = (await session.execute(select(Permiso))).scalars().all()
        permisos_dict = {p.codigo: p for p in permisos_db}

        print("\n[+] Sembrando Roles...")
        roles_data = ["SUPER_ADMIN", "ADMIN_TALLER", "ADMIN_SUCURSAL", "SUPERVISOR", "OPERADOR", "MECANICO", "CLIENTE"]
        roles_dict = {}
        for role_name in roles_data:
            existing = (await session.execute(select(Rol).where(Rol.nombre == role_name))).scalar_one_or_none()
            if not existing:
                rol = await Rol.create(session, obj_in={"nombre": role_name})
                print(f"  - Creado rol: {role_name}")
                roles_dict[role_name] = rol
            else:
                print(f"  - Rol existente: {role_name}")
                roles_dict[role_name] = existing
                
        # Asignar permisos a roles
        print("\n[+] Asignando Permisos a Roles...")
        asignaciones = {
            "SUPER_ADMIN": [p for p in permisos_data], # Todo incluyendo SAAS
            "ADMIN_TALLER": [p for p in permisos_data if p[0] != "PERMISO_GESTIONAR_SAAS"], # Todo menos SAAS
            "ADMIN_SUCURSAL": [
                ("PERMISO_VER_DASHBOARD", ""),
                ("PERMISO_VER_REPORTES", ""),
                ("PERMISO_VER_TECNICO", ""),
                ("PERMISO_GESTIONAR_TECNICO", ""),
                ("PERMISO_VER_TRABAJOS", ""),
                ("PERMISO_GESTIONAR_TRABAJOS", "")
                # Excluye PERMISO_GESTIONAR_SUCURSALES y SAAS
            ],
            "SUPERVISOR": [
                ("PERMISO_VER_DASHBOARD", ""),
                ("PERMISO_VER_REPORTES", ""),
                ("PERMISO_VER_TECNICO", ""),
                ("PERMISO_VER_TRABAJOS", ""),
                ("PERMISO_GESTIONAR_TRABAJOS", "")
            ],
            "OPERADOR": [
                ("PERMISO_VER_DASHBOARD", ""),
                ("PERMISO_VER_TRABAJOS", ""),
                ("PERMISO_GESTIONAR_TRABAJOS", "")
            ]
        }
        
        for rol_nombre, perms in asignaciones.items():
            rol = roles_dict[rol_nombre]
            for cod, _ in perms:
                permiso = permisos_dict[cod]
                # Check si ya tiene el permiso
                exists_rp = (await session.execute(
                    select(RolPermiso).where(RolPermiso.id_rol == rol.id, RolPermiso.id_permiso == permiso.id)
                )).scalar_one_or_none()
                if not exists_rp:
                    rp = RolPermiso(id_rol=rol.id, id_permiso=permiso.id)
                    session.add(rp)
        
        print("\n[+] Sembrando Planes de Suscripción...")
        planes_data = [
            {"nombre": "Gratuita", "descripcion": "Plan básico gratuito", "precio_mensual": 0.0, "max_sucursales": 1, "max_tecnicos": 5, "max_admins_sucursal": 1},
            {"nombre": "Standar", "descripcion": "Plan estándar para negocios en crecimiento", "precio_mensual": 29.99, "max_sucursales": 3, "max_tecnicos": 15, "max_admins_sucursal": 2},
            {"nombre": "Profesional", "descripcion": "Plan para talleres profesionales con múltiples ubicaciones", "precio_mensual": 79.99, "max_sucursales": 10, "max_tecnicos": 50, "max_admins_sucursal": 5},
            {"nombre": "Deluxe", "descripcion": "Plan ilimitado para grandes corporaciones", "precio_mensual": 199.99, "max_sucursales": 9999, "max_tecnicos": 9999, "max_admins_sucursal": 9999},
        ]
        
        for plan in planes_data:
            existing = (await session.execute(select(PlanSuscripcion).where(PlanSuscripcion.nombre == plan["nombre"]))).scalar_one_or_none()
            if not existing:
                plan_db = await PlanSuscripcion.create(session, obj_in=plan)
                print(f"  - Creado plan: {plan['nombre']}")
            else:
                plan_db = existing
                print(f"  - Plan existente: {plan['nombre']}")
                
            # Asignar permisos al plan
            for cod, _ in permisos_data:
                if cod == "PERMISO_GESTIONAR_SAAS":
                    continue
                permiso = permisos_dict[cod]
                exists_pp = (await session.execute(
                    select(PlanPermiso).where(PlanPermiso.id_plan == plan_db.id, PlanPermiso.id_permiso == permiso.id)
                )).scalar_one_or_none()
                if not exists_pp:
                    pp = PlanPermiso(id_plan=plan_db.id, id_permiso=permiso.id)
                    session.add(pp)

        await session.commit()
        print("\n✅ Permisos, Planes y Roles generados correctamente.")

if __name__ == "__main__":
    asyncio.run(seed_planes_y_roles())
