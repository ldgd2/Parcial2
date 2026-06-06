import asyncio
import questionary
from sqlalchemy import select
from .db_utils import AsyncSessionLocal, Emergencia, get_clientes, get_talleres

async def seed_emergencias_inteligentes():
    print("\n[+] Generando Emergencia Inteligente...")
    
    clientes = await get_clientes()
    talleres = await get_talleres()
    
    if not clientes or not talleres:
        print("❌ [BLOQUEO RELACIONAL] No puedes crear una emergencia si no hay Clientes y Talleres registrados.")
        print("💡 Por favor, utiliza el wizard para crear al menos un Cliente y un Taller primero.")
        return
        
    choices_clientes = [{"name": f"{c.nombre} ({c.correo})", "value": c.id} for c in clientes]
    cliente_id = await questionary.select("Selecciona el Cliente que reporta:", choices=choices_clientes).ask_async()
    
    choices_talleres = [{"name": f"{t.nombre} ({t.cod})", "value": t.id} for t in talleres]
    taller_id = await questionary.select("Selecciona el Taller asignado:", choices=choices_talleres).ask_async()
    
    if not cliente_id or not taller_id:
        return
        
    descripcion = await questionary.text("Descripción del problema reportado por el cliente:").ask_async()
    
    async with AsyncSessionLocal() as session:
        # Aquí normalmente invocaríamos la IA para el resumen, pero al ser un seed directo simulamos o creamos la entidad.
        # Por simplicidad y asegurar que la base de datos se pueble, insertamos la emergencia.
        
        # Necesitamos Estado y Prioridad
        from .db_utils import Estado, Prioridad
        estado_reportado = (await session.execute(select(Estado).filter_by(nombre="REPORTADO"))).scalars().first()
        prioridad_media = (await session.execute(select(Prioridad).filter_by(descripcion="Prioridad media"))).scalars().first()
        
        if not estado_reportado or not prioridad_media:
            print("❌ Falta seed base de Estados y Prioridades. Esto se creará en el refactor principal.")
            # Crear si no existen como fallback (procedimental)
            if not estado_reportado:
                estado_reportado = Estado(nombre="REPORTADO", descripcion="Emergencia reportada")
                session.add(estado_reportado)
            if not prioridad_media:
                prioridad_media = Prioridad(descripcion="Prioridad media")
                session.add(prioridad_media)
            await session.commit()
            
        emergencia = Emergencia(
            idCliente=cliente_id,
            idTaller=taller_id,
            descripcion_cliente=descripcion,
            idEstado=estado_reportado.id,
            idPrioridad=prioridad_media.id,
            latitud=-17.7833,
            longitud=-63.1821
        )
        session.add(emergencia)
        await session.commit()
        
        print(f"\n✅ Emergencia para cliente {cliente_id} en taller {taller_id} creada exitosamente (ID: {emergencia.id}).")

if __name__ == "__main__":
    asyncio.run(seed_emergencias_inteligentes())
