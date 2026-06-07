import asyncio
import os
import sys

_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
_backend_path = os.path.join(_root_dir, 'backend')
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)

from sqlalchemy import text
import subprocess

async def force_stamp():
    try:
        from app.db.session import engine
        
        print("Borrando tabla de versiones corrupta (alembic_version)...")
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE;"))
            
        print("Tabla borrada. Estampando a HEAD limpio...")
        alembic_exe_list = [sys.executable, "-m", "alembic"]
        subprocess.run([*alembic_exe_list, "stamp", "head"], cwd=_backend_path, check=True)
        print("¡Base de datos estampada exitosamente a la última versión!")
    except Exception as e:
        print(f"[ERROR] No se pudo forzar el stamp: {e}")

if __name__ == "__main__":
    asyncio.run(force_stamp())
