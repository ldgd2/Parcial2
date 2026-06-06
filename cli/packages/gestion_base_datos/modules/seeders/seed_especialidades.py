import asyncio
from sqlalchemy import select
from .db_utils import AsyncSessionLocal, Especialidad

async def seed_especialidades_mecanicas():
    async with AsyncSessionLocal() as session:
        print("\n[+] Sembrando Especialidades Mecánicas...")
        especialidades_data = [
            {"nombre": "Mecánica General", "descripcion": "Reparaciones mecánicas"},
            {"nombre": "Electricidad", "descripcion": "Sistema eléctrico"},
            {"nombre": "Neumáticos", "descripcion": "Cambio y reparación de llantas"},
            {"nombre": "Frenos", "descripcion": "Sistema de frenos"},
            {"nombre": "Aire Acondicionado", "descripcion": "Sistema A/C"},
            {"nombre": "Pintura", "descripcion": "Trabajos de pintura"},
        ]
        
        for esp_data in especialidades_data:
            existing = (await session.execute(select(Especialidad).filter_by(nombre=esp_data["nombre"]))).scalars().first()
            if not existing:
                esp = Especialidad(**esp_data)
                session.add(esp)
                print(f"  - Creada especialidad: {esp_data['nombre']}")
            else:
                print(f"  - Especialidad existente: {esp_data['nombre']}")

        await session.commit()
        print("\n✅ Especialidades generadas correctamente.")

if __name__ == "__main__":
    asyncio.run(seed_especialidades_mecanicas())
