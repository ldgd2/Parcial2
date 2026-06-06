import asyncio
import questionary
from sqlalchemy import select
from .db_utils import AsyncSessionLocal, Taller, get_planes

async def seed_nuevo_taller():
    planes = await get_planes()
    if not planes:
        print("❌ No hay planes de suscripción. Genera los planes primero.")
        return
        
    choices = [{"name": f"{p.nombre} (${p.precio_mensual})", "value": p.id} for p in planes]
    
    plan_id = await questionary.select(
        "Selecciona el plan para este Taller:",
        choices=choices
    ).ask_async()
    
    if not plan_id:
        return
        
    cod = await questionary.text("Código del Taller (Ej. T001):").ask_async()
    nombre = await questionary.text("Nombre del Taller:").ask_async()
    direccion = await questionary.text("Dirección:").ask_async()
    
    if not cod or not nombre:
        return

    async with AsyncSessionLocal() as session:
        existing = (await session.execute(select(Taller).filter_by(cod=cod))).scalars().first()
        if existing:
            print(f"❌ El taller con código {cod} ya existe.")
            return
            
        taller = Taller(
            cod=cod,
            nombre=nombre,
            direccion=direccion,
            latitud=-17.7833, # Default
            longitud=-63.1821,
            estado="ACTIVO",
            plan_id=plan_id
        )
        session.add(taller)
        await session.commit()
        print(f"\n✅ Taller '{nombre}' creado exitosamente bajo el plan ID {plan_id}.")

if __name__ == "__main__":
    asyncio.run(seed_nuevo_taller())
