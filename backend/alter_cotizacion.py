import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")

async def main():
    print(f"Using DB: {DATABASE_URL}")
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        print("Modificando tabla cotizacion...")
        try:
            await conn.execute("ALTER TABLE public.cotizacion ADD COLUMN moneda VARCHAR(3) DEFAULT 'BOB' NOT NULL")
            await conn.execute("ALTER TABLE public.cotizacion ADD COLUMN lista_productos JSON DEFAULT '[]' NOT NULL")
            await conn.execute("ALTER TABLE public.cotizacion ADD COLUMN lista_servicios JSON DEFAULT '[]' NOT NULL")
            await conn.execute("ALTER TABLE public.cotizacion ADD COLUMN subtotal_productos FLOAT DEFAULT 0.0 NOT NULL")
            await conn.execute("ALTER TABLE public.cotizacion ADD COLUMN subtotal_servicios FLOAT DEFAULT 0.0 NOT NULL")
            await conn.execute("ALTER TABLE public.cotizacion ADD COLUMN total_general FLOAT DEFAULT 0.0 NOT NULL")
            print("Columnas agregadas con éxito.")
        except Exception as e:
            print("Error agregando columnas (puede que ya existan):", e)
            
        try:
            await conn.execute("ALTER TABLE public.cotizacion DROP COLUMN costo_mano_obra")
            await conn.execute("ALTER TABLE public.cotizacion DROP COLUMN costo_repuestos")
            print("Columnas antiguas eliminadas con éxito.")
        except Exception as e:
            print("Error eliminando columnas (puede que ya se hayan borrado):", e)
            
        try:
            await conn.execute("ALTER TABLE public.cotizacion ALTER COLUMN descripcion_servicio DROP NOT NULL")
            print("descripcion_servicio ahora es NULLable.")
        except Exception as e:
            print("Error modificando descripcion_servicio:", e)

    print("Proceso completado.")

if __name__ == "__main__":
    asyncio.run(main())
