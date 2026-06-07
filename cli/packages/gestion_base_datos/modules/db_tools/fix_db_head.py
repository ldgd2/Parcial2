import asyncio
import os
import sys

# Setup paths (2 levels from menu.py which is at cli/packages/gestion_base_datos)
# We are currently in cli/packages/gestion_base_datos/modules/db_tools
_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
_backend_path = os.path.join(_root_dir, 'backend')
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)

from sqlalchemy import text

async def force_stamp():
    try:
        from app.db.session import engine
        
        print("Borrando tabla de versiones corrupta (alembic_version)...")
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE;"))
            
        print("Tabla borrada.")
    except Exception as e:
        print(f"[ERROR] No se pudo borrar la tabla: {e}")

if __name__ == "__main__":
    asyncio.run(force_stamp())
