import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import AsyncSessionLocal
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.models.resumen_ia import ResumenIA
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.services.ai_service import analizar_transcripcion_whisper
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.categoria_repo import CategoriaRepo
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.prioridad_repo import PrioridadRepo

logger = logging.getLogger(__name__)

async def ia_queue_worker_loop():
    """
    Background worker loop that checks every 60 seconds for emergencies
    where the AI failed (diagnostico_probable == 'PENDIENTE_REINTENTO_IA')
    and retries processing them.
    """
    logger.info("Iniciando IA Queue Worker (Polling cada 60s)...")
    while True:
        try:
            await process_pending_ia_emergencies()
        except asyncio.CancelledError:
            logger.info("IA Queue Worker detenido.")
            break
        except Exception as e:
            logger.error(f"Error en IA Queue Worker: {e}")
        
        await asyncio.sleep(60)

async def process_pending_ia_emergencies():
    async with AsyncSessionLocal() as db:
        # Encontrar emergencias que tienen PENDIENTE_REINTENTO_IA
        # Usamos filter y json extract o buscamos en ResumenIA
        stmt = (
            select(Emergencia)
            .join(ResumenIA, Emergencia.id == ResumenIA.idEmergencia)
            .options(selectinload(Emergencia.evidencias), selectinload(Emergencia.resumen_ia))
        )
        result = await db.execute(stmt)
        emergencias = result.scalars().all()
        
        for emg in emergencias:
            if not emg.resumen_ia:
                continue
                
            ficha = emg.resumen_ia.FichaTecnica
            if isinstance(ficha, dict) and ficha.get("diagnostico_probable") == "PENDIENTE_REINTENTO_IA":
                logger.info(f"Reintentando IA para emergencia ID: {emg.id}")
                
                # Fetch categories and priorities for context
                cat_repo = CategoriaRepo(db)
                pri_repo = PrioridadRepo(db)
                categorias = [{"id": c.id, "nombre": c.descripcion} for c in await cat_repo.get_all()]
                prioridades = [{"id": p.id, "nombre": p.descripcion} for p in await pri_repo.get_all()]
                
                # Armar texto
                texto_crudo = emg.texto_adicional or emg.descripcion
                
                # Obtener imagenes
                evidencias_urls = [e.url for e in emg.evidencias if e.url]
                
                try:
                    analisis = await analizar_transcripcion_whisper(
                        texto_crudo=texto_crudo,
                        categorias_disponibles=categorias,
                        prioridades_disponibles=prioridades,
                        vehiculo_info=f"Placa: {emg.placaVehiculo}",
                        evidencias_urls=evidencias_urls
                    )
                    
                    # Update if valid
                    if analisis.ficha_tecnica.diagnostico_probable != "PENDIENTE_REINTENTO_IA":
                        emg.resumen_ia.Resumen = analisis.resumen_taller
                        emg.resumen_ia.FichaTecnica = analisis.ficha_tecnica.model_dump()
                        emg.resumen_ia.recomendaciones_taller = analisis.recomendaciones_taller
                        emg.resumen_ia.motivo_rechazo = analisis.motivo_rechazo
                        
                        emg.idCategoria = analisis.id_categoria
                        emg.idPrioridad = analisis.id_prioridad
                        
                        await db.commit()
                        logger.info(f"✅ Emergencia {emg.id} procesada exitosamente en reintento.")
                    else:
                        logger.warning(f"⚠️ Emergencia {emg.id} reintento fallido, sigue en cola.")
                except Exception as ex:
                    logger.error(f"Error procesando reintento IA para emergencia {emg.id}: {ex}")
                    await db.rollback()
