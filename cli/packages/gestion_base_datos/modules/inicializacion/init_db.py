import asyncio
import platform
import asyncpg
import warnings
from app.db.session import engine
from app.core.config import settings
from app.db.base import Base  # Esto carga todos los modelos para Alembic y SQLAlchemy

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
    
    # Primero probamos si existe conectando a 'postgres'
    try:
        conn = await asyncpg.connect(database="postgres", **conn_params)
        exists = await conn.fetchval(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        if not exists:
            print(f"Base de datos '{db_name}' no existe. Creándola...")
            # CREATE DATABASE no se puede ejecutar en transacciones
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"[OK] Base de datos '{db_name}' creada.")
        await conn.close()
    except Exception as e:
        print(f"[WARNING] No se pudo verificar/crear la DB via 'postgres': {e}")

async def init_db():
    await check_and_create_db()
    
    print(f"Inicializando tablas en '{settings.DB_NAME}'...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tablas creadas correctamente.")


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(init_db())
