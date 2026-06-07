import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# ID del fix. Útil para mantener un registro en una tabla de fixes si lo desean, 
# pero por ahora se ejecuta idempotentemente.
FIX_ID = "001"
FIX_DESCRIPTION = "Asignar idEspecialidad a las Categorias de Problemas (Radar Fix)"

async def run_fix(db: AsyncSession):
    print(f"🔧 Ejecutando Fix {FIX_ID}: {FIX_DESCRIPTION}...")
    
    # Este query asume que idEspecialidad tiene el mismo ID que idCategoria en la data base actual,
    # o bien podemos forzar el mapeo exacto de los seeders
    queries = [
        "UPDATE public.categoria_problema SET \"idEspecialidad\" = 1 WHERE descripcion = 'Problema de Batería';",
        "UPDATE public.categoria_problema SET \"idEspecialidad\" = 1 WHERE descripcion = 'Falla de Motor';",
        "UPDATE public.categoria_problema SET \"idEspecialidad\" = 2 WHERE descripcion = 'Falla de Frenos';",
        "UPDATE public.categoria_problema SET \"idEspecialidad\" = 3 WHERE descripcion = 'Problema de Neumáticos';",
        "UPDATE public.categoria_problema SET \"idEspecialidad\" = 4 WHERE descripcion = 'Problema de Suspensión';",
        "UPDATE public.categoria_problema SET \"idEspecialidad\" = 5 WHERE descripcion = 'Problema de Transmisión';",
        "UPDATE public.categoria_problema SET \"idEspecialidad\" = 6 WHERE descripcion = 'Problema de Aire Acondicionado';",
        "UPDATE public.categoria_problema SET \"idEspecialidad\" = 1 WHERE descripcion = 'Problema de Sistema Eléctrico';",
        "UPDATE public.categoria_problema SET \"idEspecialidad\" = 5 WHERE descripcion = 'Otros';"
    ]
    
    for q in queries:
        await db.execute(text(q))
    await db.commit()
    print(f"✅ Fix {FIX_ID} aplicado exitosamente.")

if __name__ == "__main__":
    # Si se ejecuta directamente (standalone)
    import sys
    import os
    # Añadir backend al PYTHONPATH si no está
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "backend"))
    if backend_dir not in sys.path:
        sys.path.append(backend_dir)
        
    from app.db.session import AsyncSessionLocal
    
    async def main():
        async with AsyncSessionLocal() as db:
            await run_fix(db)
            
    asyncio.run(main())
