import asyncio
import os
import sys
from dotenv import load_dotenv

# Setup paths
_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_backend_path = os.path.join(_root_dir, 'backend')
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)

load_dotenv(os.path.join(_root_dir, ".env"))

try:
    from app.db.session import AsyncSessionLocal
    from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
    from app.packages.gestion_usuarios_seguridad.modules.tenants.models.especialidad import Especialidad
    from app.packages.gestion_usuarios_seguridad.modules.tenants.models.asignacion_especialidad import AsignacionEspecialidad
    from sqlalchemy import select
except ImportError as e:
    print(f"[ERROR] No se pudo importar los módulos de la aplicación: {e}")
    sys.exit(1)

async def fix_specialties():
    print("Herramienta de Reparación: Asignación Masiva de Especialidades...")
    async with AsyncSessionLocal() as db:
        # 1. Obtener todos los talleres
        talleres_res = await db.execute(select(Taller))
        talleres = talleres_res.scalars().all()
        
        # 2. Obtener todas las especialidades
        esp_res = await db.execute(select(Especialidad))
        especialidades = esp_res.scalars().all()
        
        print(f"Encontrados {len(talleres)} talleres y {len(especialidades)} especialidades.")
        
        count = 0
        for t in talleres:
            print(f"Procesando taller: {t.nombre} ({t.cod})")
            for e in especialidades:
                # Verificar si ya existe
                check_res = await db.execute(
                    select(AsignacionEspecialidad).where(
                        AsignacionEspecialidad.idTaller == t.cod,
                        AsignacionEspecialidad.idEspecialidad == e.id
                    )
                )
                if not check_res.scalar_one_or_none():
                    db.add(AsignacionEspecialidad(idTaller=t.cod, idEspecialidad=e.id))
                    print(f"  + Asignada especialidad: {e.nombre}")
                    count += 1
        
        if count > 0:
            await db.commit()
            print(f"\n[OK] ¡Listo! Se crearon {count} nuevas asignaciones.")
        else:
            print("\n[INFO] Todos los talleres ya tenían todas las especialidades asignadas.")

if __name__ == "__main__":
    asyncio.run(fix_specialties())
