import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# ─── Configuración de la App ──────────────────────────────────────
from app.core.config import settings
from app.db.base import Base

# object that provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    # Asegurar que el driver sea de PostgreSQL asíncrono
    url = settings.DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

from sqlalchemy import text

def include_name(name, type_, parent_names):
    if type_ == "table" and name == "alembic_version":
        return False
    return True

def do_run_migrations(connection: Connection, tenant_schema: str = "public") -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=tenant_schema,
        include_schemas=True,
        include_name=include_name,
    )
    with context.begin_transaction():
        if tenant_schema != "public":
            context.execute(f"SET search_path TO {tenant_schema}")
        context.run_migrations()
        if tenant_schema != "public":
            context.execute("SET search_path TO public")

async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        import sys
        is_autogenerate = any(arg == "--autogenerate" for arg in sys.argv)
        
        # Run migrations on public schema
        await connection.run_sync(do_run_migrations, "public")
        
        # We skip migrating tenant schemas because ALL models are currently
        # hardcoded to __table_args__ = {"schema": "public"}. Running migrations
        # on empty tenant schemas causes constraint dropping errors since the
        # tables only exist in public.

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    import platform
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
