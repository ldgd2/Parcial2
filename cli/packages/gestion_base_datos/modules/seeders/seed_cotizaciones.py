import asyncio
import questionary
from sqlalchemy import select
from .db_utils import AsyncSessionLocal, Cotizacion

async def seed_cotizaciones():
    print("\n[+] Generando Cotización...")
    
    async with AsyncSessionLocal() as session:
        from .db_utils import Emergencia
        emergencias = (await session.execute(select(Emergencia))).scalars().all()
        
        if not emergencias:
            print("❌ [BLOQUEO RELACIONAL] No hay emergencias registradas en el sistema.")
            print("💡 No se puede crear una cotización en el vacío. Registra una emergencia primero.")
            return
            
        choices_em = [{"name": f"Emergencia #{e.id} - Taller: {e.idTaller}", "value": e.id} for e in emergencias]
        emergencia_id = await questionary.select("Selecciona la emergencia a cotizar:", choices=choices_em).ask_async()
        
        if not emergencia_id: return
        
        monto_str = await questionary.text("Monto total de la cotización (USD):", default="50.00").ask_async()
        detalles = await questionary.text("Detalles de repuestos y mano de obra:").ask_async()
        
        cotizacion = Cotizacion(
            idEmergencia=emergencia_id,
            monto_total=float(monto_str),
            detalles=detalles,
            estado="PENDIENTE"
        )
        session.add(cotizacion)
        await session.commit()
        print(f"\n✅ Cotización por ${monto_str} creada para la emergencia #{emergencia_id}.")

if __name__ == "__main__":
    asyncio.run(seed_cotizaciones())
