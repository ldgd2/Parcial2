from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Motor asíncrono de SQLAlchemy
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Fábrica de sesiones
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Base declarativa compartida por todos los modelos."""
    pass


from fastapi import Request
from sqlalchemy import text

# ─── Dependencia FastAPI ──────────────────────────────────────────
async def get_db(request: Request = None) -> AsyncSession:
    """Inyecta una sesión de base de datos en cada request, manejando el multitenancy."""
    async with AsyncSessionLocal() as session:
        try:
            if request:
                tenant_schema = request.headers.get("X-Tenant-Schema")
                if tenant_schema:
                    # Sanitizamos el input básico
                    if tenant_schema.isidentifier():
                        await session.execute(text(f"SET search_path TO {tenant_schema}, public"))
            
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
