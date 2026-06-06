import sys
import os
import platform

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

import asyncio
import platform
import asyncpg
import warnings
from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base
from app.core.config import settings

# Silenciar el aviso de deprecación de loop policy en Python 3.14+
warnings.filterwarnings("ignore", category=DeprecationWarning)

async def check_and_create_db():
    # Conectarse a la base de datos 'postgres' para crear la DB destino si falta
    db_name = settings.DB_NAME
    conn_params = {
        "user": settings.DB_USER,
        "password": settings.DB_PASSWORD.get_secret_value() if hasattr(settings.DB_PASSWORD, 'get_secret_value') else settings.DB_PASSWORD,
        "host": settings.DB_HOST,
        "port": settings.DB_PORT,
    }
    
    try:
        conn = await asyncpg.connect(database="postgres", **conn_params)
        exists = await conn.fetchval(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        if not exists:
            print(f"Base de datos '{db_name}' no existe. Creándola...")
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"[OK] Base de datos '{db_name}' creada.")
        await conn.close()
    except Exception as e:
        print(f"[WARNING] No se pudo verificar/crear la DB via 'postgres': {e}")

async def hard_reset_db():
    await check_and_create_db()
    print("[!] INICIANDO DESTRUCCIÓN DE LA BASE DE DATOS...")
    
    try:
        async with engine.begin() as conn:
            # Drop all tenant schemas dynamically
            print(">> Buscando esquemas de tenants...")
            result = await conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'public') AND schema_name NOT LIKE 'pg_%'"))
            tenant_schemas = [row[0] for row in result.all()]
            for ts in tenant_schemas:
                print(f">> Ejecutando DROP SCHEMA {ts} CASCADE...")
                await conn.execute(text(f"DROP SCHEMA {ts} CASCADE;"))
                
            # Borrado absoluto del cascade public schema para PostgreSQL
            print(">> Ejecutando DROP SCHEMA public CASCADE...")
            await conn.execute(text("DROP SCHEMA public CASCADE;"))
            print(">> Ejecutando CREATE SCHEMA public...")
            await conn.execute(text("CREATE SCHEMA public;"))
            print(">> Restaurando privilegios...")
            await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
            await conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
    except Exception as e:
        print(f"[ERROR] No se pudo resetear la base de datos: {e}")
        # En Windows a veces la conexión se cierra al dropear el schema si hay bloqueos
        sys.exit(1)

    print("[OK] Tablas Destruidas y limpiadas.")

if __name__ == "__main__":
    # FIX para Windows: asyncpg + ProactorEventLoop suele dar WinError 64 o 10054
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(hard_reset_db())
