import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def run():
    async with AsyncSessionLocal() as db:
        query = """
        SELECT e.id, e."idEstado", c."idEspecialidad", e."idTaller", e.es_valida
        FROM emergencia e
        JOIN categoria_problema c ON c.id = e."idCategoria"
        WHERE e.id >= 20
        """
        res = await db.execute(text(query))
        print("Emergencias >= 20:", res.all())

        query2 = """
        SELECT e.id
        FROM public.emergencia e 
        JOIN public.categoria_problema c ON c.id = e."idCategoria"
        WHERE e."idTaller" IS NULL 
        AND e."idEstado" IN (3, 1) 
        AND e.es_valida IS true 
        AND c."idEspecialidad" IN (1, 2, 3, 4, 5, 6)
        """
        res2 = await db.execute(text(query2))
        print("Query Radar exacto:", res2.all())

asyncio.run(run())
