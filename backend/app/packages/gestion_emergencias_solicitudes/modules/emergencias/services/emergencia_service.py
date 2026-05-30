"""
Servicio de Emergencias — CU04, CU14, CU15
  CU04: Reportar emergencia (cliente)
  CU14: Consultar mis solicitudes (cliente)
  CU15: Gestionar solicitud taller (taller — aceptar/rechazar/actualizar estado)
"""
import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.vehiculo import Vehiculo
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.emergencia import EmergenciaCreate, EmergenciaOut, ActualizarEstadoRequest
from app.core.config import settings

# Repositories
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.emergencia_repo import EmergenciaRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.estado_repo import EstadoRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.prioridad_repo import PrioridadRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.categoria_repo import CategoriaProblemaRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.evidencia_repo import EvidenciaRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.historial_repo import HistorialEstadoRepository
from app.packages.gestion_emergencias_solicitudes.modules.auxilio_solicitudes.repositories.asignacion_repo import AsignacionTecnicoEmergenciaRepository
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.repositories.resumen_ia_repo import ResumenIARepository
from app.packages.gestion_administrativa_reportes.modules.pagos.repositories.pago_repo import PagoRepository
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.repositories.vehiculo_repo import VehiculoRepository
from app.packages.gestion_usuarios_seguridad.modules.tenants.repositories.taller_repo import TallerRepository
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.services.ai_service import analizar_transcripcion_whisper
from typing import List
import math
from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.services.notification_service import NotificationService


# ─── CU04 ─────────────────────────────────────────────────────────

async def reportar_emergencia(
    data: EmergenciaCreate,
    cliente_id: int,
    db: AsyncSession,
) -> EmergenciaOut:
    # Validar que el vehículo pertenece al cliente y obtener datos para la IA
    vehiculo_repo = VehiculoRepository(db)
    vehiculo = await vehiculo_repo.get_by_placa(data.placaVehiculo)
    if vehiculo is None or vehiculo.idCliente != cliente_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado o no pertenece al cliente.",
        )

    # Contexto del vehículo para la IA
    vehiculo_contexto = f"{vehiculo.marca} {vehiculo.modelo} {vehiculo.anio} (Placa: {vehiculo.placa})"

    # Valores por defecto para el reporte inicial (CU11 - Desacoplado)
    # Estos valores pueden ser sobrescritos por el análisis de IA más adelante.
    prioridad_id = 1  # BAJA por defecto
    categoria_id = 5  # OTROS por defecto (ajustar según seed)
    resumen_taller = ""
    ficha_tecnica = None

    # CU08, CU09, CU10: IA processing si hay contenido para analizar
    print(f"Evaluando IA: desc={bool(data.descripcion)}, texto_ad={bool(data.texto_adicional)}, fotos={len(data.evidencias_urls)}")
    if data.descripcion or data.texto_adicional or data.evidencias_urls:
        try:
            # Obtener catálogos para el prompt de IA
            categoria_repo = CategoriaProblemaRepository(db)
            prioridad_repo = PrioridadRepository(db)
            
            categorias = await categoria_repo.get_all()
            prioridades = await prioridad_repo.get_all()
            
            categorias_activas = [{"id": r.id, "nombre": r.descripcion} for r in categorias]
            prioridades_activas = [{"id": r.id, "nombre": r.descripcion} for r in prioridades]

            # Construir URLs completas
            # Si el path ya empieza con uploads/, no lo duplicamos
            base_url_simple = f"http://{settings.APP_HOST}:8000"
            full_urls = []
            for u in data.evidencias_urls:
                if u.startswith('http'):
                    full_urls.append(u)
                elif u.startswith('uploads/'):
                    full_urls.append(f"{base_url_simple}/{u}")
                else:
                    full_urls.append(f"{base_url_simple}/uploads/{u}")

            print(f"🖼️ URLs enviadas a IA: {full_urls}")

            # Combinar descripción y texto adicional para mejor contexto
            texto_para_ia = data.texto_adicional or data.descripcion
            if data.texto_adicional and data.descripcion and data.texto_adicional != data.descripcion:
                texto_para_ia = f"{data.descripcion}. {data.texto_adicional}"

            # Llamada al servicio de IA OpenRouter + Instructor (Multi-modal)
            ia_result = await analizar_transcripcion_whisper(
                texto_crudo=texto_para_ia,
                vehiculo_info=vehiculo_contexto,
                categorias_disponibles=categorias_activas,
                prioridades_disponibles=prioridades_activas,
                evidencias_urls=full_urls
            )

            # Reemplazar valores base con los dictaminados por la IA
            prioridad_id = ia_result.id_prioridad
            categoria_id = ia_result.id_categoria
            resumen_taller = ia_result.resumen_taller
            # Usar el título generado por la IA en lugar de la descripción del usuario
            if ia_result.titulo_emergencia:
                data.descripcion = ia_result.titulo_emergencia
            ficha_tecnica = ia_result.ficha_tecnica.model_dump()
        except Exception as e:
            print(f"Error procesando IA: {e}")
            # Si la IA falla, usamos los defaults y seguimos sin interrumpir la emergencia crítica

    # Crear emergencia
    repo = EmergenciaRepository(db)
    emergencia = await repo.create(obj_in={
        "descripcion": data.descripcion,
        "texto_adicional": data.texto_adicional,
        "direccion": data.direccion,
        "latitud": data.latitud,
        "longitud": data.longitud,
        "fecha": datetime.date.today(),
        "hora": data.hora,
        "idTaller": None,
        "idPrioridad": prioridad_id,
        "idCategoria": categoria_id,
        "idCliente": cliente_id,
        "placaVehiculo": data.placaVehiculo,
        "audio_url": data.audio_url,
        "es_valida": True # Se actualizará abajo si la IA lo dice
    })
    await db.flush()

    # CU05: Crear pago inicial en 0 para evitar nulos (Modo Failsafe)
    pago_repo = PagoRepository(db)
    await pago_repo.create(obj_in={
        "monto": 0.0,
        "monto_comision": 0.0,
        "cliente_id": cliente_id,
        "emergencia_id": emergencia.id,
        "estado": "PENDIENTE"
    })
    await db.flush()

    # Guardar Evidencias (Fotos)
    evidencia_repo = EvidenciaRepository(db)
    for url in data.evidencias_urls:
        await evidencia_repo.create(obj_in={
            "direccion": url,
            "idEmergencia": emergencia.id
        })
    await db.flush()

    # Guardar análisis IA si fue procesado
    if resumen_taller:
        resumen_repo = ResumenIARepository(db)
        await resumen_repo.create(obj_in={
            "resumen": resumen_taller,
            "ficha_tecnica": ficha_tecnica,
            "recomendaciones_taller": ia_result.recomendaciones_taller if 'ia_result' in locals() else None,
            "motivo_rechazo": ia_result.motivo_rechazo if 'ia_result' in locals() else None,
            "idEmergencia": emergencia.id
        })
        if 'ia_result' in locals():
            await repo.update(db_obj=emergencia, obj_in={"es_valida": ia_result.es_valida})
            
            if not ia_result.es_valida:
                try:
                    await NotificationService.enviar_notificacion_usuario(
                        db=db,
                        user_id=cliente_id,
                        titulo="Reporte Requiere Corrección",
                        cuerpo=f"La IA no pudo validar tu reporte: {ia_result.motivo_rechazo}. Por favor, corrige los datos o cancela.",
                        data={
                            "tipo": "emergencia_invalida",
                            "emergencia_id": str(emergencia.id),
                            "motivo": ia_result.motivo_rechazo
                        }
                    )
                except Exception as e:
                    print(f"Error enviando notificacion de rechazo IA: {e}")
        
        await db.flush()


    estado_repo = EstadoRepository(db)
    estado = await estado_repo.get_by_nombre("PENDIENTE")
    if estado is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Estado 'PENDIENTE' no encontrado en BD. Ejecute el seed inicial.",
        )

    await repo.update(db_obj=emergencia, obj_in={"idEstado": estado.id})
    historial_repo = HistorialEstadoRepository(db)
    await historial_repo.create(obj_in={
        "idEmergencia": emergencia.id,
        "idEstado": estado.id,
    })
    await db.commit()

    return await obtener_emergencia_detalle(emergencia.id, db)

async def obtener_emergencia_detalle(id: int, db: AsyncSession):
    repo = EmergenciaRepository(db)
    emergencia = await repo.get_detalle_by_id(id)
    if emergencia:
        _populate_dynamic_fields(emergencia)
    return emergencia

def _populate_dynamic_fields(e: Emergencia):
    """Calcula campos que no estn en la tabla base para el esquema de salida."""
    if e.historial:
        last_h = sorted(e.historial, key=lambda x: (x.fecha_cambio, x.id), reverse=True)[0]
        e.estado_actual = last_h.estado.nombre
    else:
        e.estado_actual = "DESCONOCIDO"

    # 2. Mutex (is_locked)
    e.is_locked = False
    if e.locked_by and e.locked_at:
        diff = datetime.datetime.now() - e.locked_at
        if diff.total_seconds() < 120:
            e.is_locked = True


# ─── CU14 (cliente consulta sus emergencias) ──────────────────────

async def listar_emergencias_cliente(cliente_id: int, db: AsyncSession):
    repo = EmergenciaRepository(db)
    emergencias = await repo.get_by_cliente(cliente_id)
    for e in emergencias:
        _populate_dynamic_fields(e)
    return emergencias


# ─── CU15 (taller actualiza el estado de la emergencia) ──────────

async def actualizar_estado_emergencia(
    emergencia_id: int,
    data: ActualizarEstadoRequest,
    taller_cod: str,
    db: AsyncSession,
):
    repo = EmergenciaRepository(db)
    emergencia = await repo.get(emergencia_id)
    if not emergencia or emergencia.idTaller != taller_cod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergencia no encontrada o no asignada a este taller.",
        )

    # Verificar que el estado existe
    estado_repo = EstadoRepository(db)
    estado = await estado_repo.get(data.idEstado)
    if estado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estado no válido.",
        )

    emergencia = await repo.update(db_obj=emergencia, obj_in={"idEstado": data.idEstado})
    historial_repo = HistorialEstadoRepository(db)
    nuevo_historial = await historial_repo.create(obj_in={
        "idEmergencia": emergencia_id,
        "idEstado": data.idEstado
    })
    await db.flush()

    # NOTIFICACIÓN AL CLIENTE (CU12)
    try:
        # Obtener nombre del nuevo estado para el mensaje
        estado_nombre = estado.nombre
        await NotificationService.enviar_notificacion_usuario(
            db, 
            emergencia.idCliente, 
            "Actualización de Servicio", 
            f"Tu reporte '{emergencia.descripcion}' ahora está: {estado_nombre}",
            {"emergencia_id": str(emergencia_id), "tipo": "estado_change"}
        )
        
        # [CU15] WebSockets en Tiempo Real
        from app.core.socket_manager import manager
        room_id = f"emergencia_{emergencia_id}"
        await manager.broadcast_to_room(room_id, {
            "type": "status_update",
            "estado": estado_nombre,
            "message": f"El técnico actualizó el estado a {estado_nombre}"
        })
        
    except Exception as e:
        print(f"Error al enviar notificación: {e}")

    return nuevo_historial


# CU15 (taller actualiza el estado de la emergencia) ──────────

async def listar_emergencias_taller(taller_cod: str, db: AsyncSession):
    repo = EmergenciaRepository(db)
    emergencias = await repo.get_by_taller(taller_cod)
    for e in emergencias:
        _populate_dynamic_fields(e)
    return emergencias


# ─── GESTIÓN DE TABLERO DE EMERGENCIAS (Admin Workshops) ──────────

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calcula la distancia en KM entre dos puntos usando la fórmula de Haversine."""
    if not all([lat1, lon1, lat2, lon2]): return 999999
    R = 6371  # Radio de la Tierra en km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c

async def listar_emergencias_disponibles(taller_cod: str, db: AsyncSession):
    """
    Lista emergencias que:
    1. No tienen taller asignado (idTaller IS NULL)
    2. El taller tiene la especialidad requerida por la categoria de la emergencia
    3. Están dentro de un radio de 50km
    """
    # 1. Obtener datos del taller
    taller_repo = TallerRepository(db)
    taller = await taller_repo.get_with_especialidades(taller_cod)
    if not taller: return []

    especialidades_taller = [a.idEspecialidad for a in taller.asignaciones]

    # 3. Buscar emergencias sin taller asignado y en estado PENDIENTE / INICIADA
    # Filtramos por especialidad requerida (match entre taller y categoria)
    estado_repo = EstadoRepository(db)
    estados_validos = []
    estado_iniciada = await estado_repo.get_by_nombre("INICIADA")
    estado_pendiente = await estado_repo.get_by_nombre("PENDIENTE")
    
    if estado_iniciada: estados_validos.append(estado_iniciada.id)
    if estado_pendiente: estados_validos.append(estado_pendiente.id)
    
    if not estados_validos:
        estados_validos = [1, 2] # Fallback
        
    repo = EmergenciaRepository(db)
    todas_disponibles = await repo.get_disponibles_para_taller(especialidades_taller, estados_validos)

    # 4. Filtrar por distancia (10km)
    cercanas = []
    for e in todas_disponibles:
        dist = haversine_distance(taller.latitud, taller.longitud, e.latitud, e.longitud)
        if dist <= 10: # Radio de 10km
            _populate_dynamic_fields(e)
            cercanas.append(e)
            
    return cercanas

async def bloquear_emergencia_temporal(emergencia_id: int, taller_cod: str, db: AsyncSession):
    """Establece un mutex temporal de 2 minutos."""
    repo = EmergenciaRepository(db)
    emergencia = await repo.get(emergencia_id)
    if not emergencia or emergencia.idTaller:
        raise HTTPException(status_code=400, detail="Emergencia no disponible para análisis.")
    
    await repo.update(db_obj=emergencia, obj_in={
        "locked_by": taller_cod,
        "locked_at": datetime.datetime.now()
    })
    await db.commit()
    return {"status": "locked", "expires_in": 120}

async def asignar_emergencia_taller(emergencia_id: int, taller_cod: str, tecnicos_ids: List[int], db: AsyncSession):
    """Asignación final con uno o varios técnicos."""
    # 1. Obtener emergencia
    repo = EmergenciaRepository(db)
    emergencia = await repo.get(emergencia_id)
    
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada.")
    
    if emergencia.idTaller and emergencia.idTaller != taller_cod:
        raise HTTPException(status_code=400, detail="Esta emergencia ya fue tomada por otro taller.")

    # 2. Realizar asignación
    await repo.update(db_obj=emergencia, obj_in={
        "idTaller": taller_cod,
        "locked_by": None,
        "locked_at": None
    })
    
    # 3. Registrar técnicos
    asignacion_repo = AsignacionTecnicoEmergenciaRepository(db)
    await asignacion_repo.delete_by_emergencia(emergencia_id)

    for t_id in tecnicos_ids:
        await asignacion_repo.create(obj_in={"idEmergencia": emergencia_id, "idTecnico": t_id})
    
    # 4. Actualizar estado a 'ASIGNADO'
    estado_repo = EstadoRepository(db)
    estado = await estado_repo.get_by_nombre("ASIGNADO")
    
    nuevo_id_estado = estado.id if estado else 2
    await repo.update(db_obj=emergencia, obj_in={"idEstado": nuevo_id_estado})
    
    historial_repo = HistorialEstadoRepository(db)
    await historial_repo.create(obj_in={
        "idEmergencia": emergencia_id,
        "idEstado": nuevo_id_estado
    })
        
    await db.commit()
    # Refrescamos para tener los datos del objeto actualizados tras el commit
    await db.refresh(emergencia)

    # 5. NOTIFICACIÓN AL CLIENTE (CU12)
    try:
        taller_repo = TallerRepository(db)
        taller = await taller_repo.get(taller_cod)
        
        # Calcular distancia y tiempo estimado
        distancia = haversine_distance(taller.latitud, taller.longitud, emergencia.latitud, emergencia.longitud)
        tiempo_estimado = round(distancia * 2.5 + 5)
        dist_str = f"{distancia:.1f} km"
        
        print(f"DEBUG: Intentando enviar notificación a Cliente {emergencia.idCliente}")
        
        await NotificationService.enviar_notificacion_usuario(
            db, 
            emergencia.idCliente, 
            "¡Ayuda en camino! 🛠️", 
            f"El taller '{taller.nombre}' ha aceptado tu solicitud. Está a {dist_str} y llegará en aprox. {tiempo_estimado} min. ¡Mantén la calma!",
            {
                "emergencia_id": str(emergencia_id), 
                "tipo": "taller_asignado",
                "distancia": dist_str,
                "tiempo": str(tiempo_estimado)
            }
        )
    except Exception as e:
        print(f"Error al enviar notificación de asignación: {e}")

    return {"status": "ok", "message": f"Emergencia asignada a {len(tecnicos_ids)} técnicos."}


# ─── CU10 — El taller actualiza la ficha técnica con datos reales ──

async def actualizar_ficha_tecnica(emergencia_id: int, data: dict, taller_cod: str, db: AsyncSession):
    """
    CU10: Generación de Ficha Técnica — El taller puede completar/corregir
    el diagnóstico, piezas y acciones con los datos reales del servicio.
    """
    # Verificar que la emergencia pertenece al taller
    repo = EmergenciaRepository(db)
    emergencia = await repo.get(emergencia_id)
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada.")
    if emergencia.idTaller != taller_cod:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta emergencia.")
    
    # Obtener o crear ResumenIA
    resumen_repo = ResumenIARepository(db)
    resumen = await resumen_repo.get_by_emergencia(emergencia_id)
    
    if resumen:
        # Actualizar ficha técnica existente (merge con datos nuevos)
        existing_ficha = resumen.ficha_tecnica or {}
        existing_ficha.update(data.get("ficha_tecnica", {}))
        
        update_data = {"ficha_tecnica": existing_ficha}
        if "resumen" in data:
            update_data["resumen"] = data["resumen"]
            
        await resumen_repo.update(db_obj=resumen, obj_in=update_data)
    else:
        # Crear resumen si no fue generado por IA
        await resumen_repo.create(obj_in={
            "resumen": data.get("resumen", "Diagnóstico completado por el taller."),
            "ficha_tecnica": data.get("ficha_tecnica", {}),
            "idEmergencia": emergencia_id
        })
    
    await db.commit()
    return {"status": "ok", "message": "Ficha técnica actualizada correctamente."}


async def finalizar_emergencia(
    emergencia_id: int,
    data: dict, # Usando dict o schema
    taller_cod: str,
    db: AsyncSession
):
    """
    Finaliza el servicio, crea el registro de pago y notifica al cliente.
    """
    from app.packages.gestion_administrativa_reportes.modules.pagos.models.pago import Pago
    
    try:
        # 1. Validar emergencia
        repo = EmergenciaRepository(db)
        emergencia = await repo.get_detalle_by_id(emergencia_id)
        
        if not emergencia:
            raise HTTPException(status_code=404, detail="Emergencia no encontrada.")
            
        if emergencia.idTaller != taller_cod:
            print(f"DEBUG 403: e.idTaller={emergencia.idTaller}, user.taller={taller_cod}")
            raise HTTPException(status_code=403, detail="No tienes acceso a esta emergencia.")

        # 2. Actualizar o Crear Pago
        factura = data.get("factura", None)
        
        if factura and isinstance(factura, dict):
            monto_raw = factura.get("total_general", data.get("monto_total", 0))
        else:
            monto_raw = data.get("monto_total", 0)
            
        try:
            monto = float(monto_raw)
        except:
            monto = 0.0
            
        comision = monto * 0.10
        
        # Log para depuración de IntegrityError
        print(f"DEBUG PAGOS: idCliente={emergencia.idCliente}, idEmergencia={emergencia_id}, monto={monto}")
        
        pago_repo = PagoRepository(db)
        if emergencia.pago:
            await pago_repo.update(db_obj=emergencia.pago, obj_in={
                "monto": monto,
                "monto_comision": comision,
                "estado": "PENDIENTE",
                "detalle_factura": factura
            })
        else:
            # Aseguramos que los IDs no sean nulos
            c_id = emergencia.idCliente
            e_id = emergencia_id
            
            if c_id is None or e_id is None:
                print(f"ERROR: No se puede crear pago con IDs nulos. c_id={c_id}, e_id={e_id}")
                raise HTTPException(status_code=500, detail="Error de integridad: Datos de cliente o emergencia faltantes.")

            await pago_repo.create(obj_in={
                "monto": monto,
                "monto_comision": comision,
                "cliente_id": c_id,
                "emergencia_id": e_id,
                "estado": "PENDIENTE",
                "detalle_factura": factura
            })
            await db.flush()
        
        # Cambiar a estado ATENDIDO (ID 6 según check_states.py)
        await repo.update(db_obj=emergencia, obj_in={"idEstado": 6})
        
        historial_repo = HistorialEstadoRepository(db)
        await historial_repo.create(obj_in={
            "idEmergencia": emergencia_id,
            "idEstado": 6,
        })
        
        await db.commit()
        
        # 4. Notificar al Cliente
        try:
            await NotificationService.enviar_notificacion_usuario(
                db,
                emergencia.idCliente,
                "¡Trabajo Terminado! ✅",
                f"El taller ha finalizado el servicio. El monto total a pagar es: ${monto:.2f}. Por favor, procede al pago.",
                {
                    "emergencia_id": str(emergencia_id),
                    "tipo": "pago_pendiente",
                    "monto": str(monto)
                }
            )
        except Exception as e:
            print(f"Error enviando notificación de finalización: {e}")

        # [CU15] Notificar finalización por WebSocket para solicitar calificación en vivo
        try:
            from app.core.socket_manager import manager
            room_id = f"emergencia_{emergencia_id}"
            await manager.broadcast_to_room(room_id, {
                "type": "solicitar_calificacion",
                "emergencia_id": emergencia_id,
                "message": "Servicio finalizado. Por favor, califica al técnico."
            })
        except Exception as e:
            print(f"Error WS finalizar_emergencia: {e}")

        return {
            "status": "ok", 
            "message": "Emergencia finalizada y cliente notificado.",
            "monto_total": monto,
            "monto_comision": comision,
            "monto_taller": monto - comision
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"Error en finalizar_emergencia: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        with open("error_log.txt", "a") as f:
            f.write("\n" + "="*50 + "\n" + error_msg + "\n")
        raise HTTPException(status_code=500, detail="Error interno del servidor al finalizar.")
async def actualizar_emergencia(id_emergencia: int, data: EmergenciaCreate, user_id: int, db: AsyncSession):
    # 1. Verificar propiedad y estado
    repo = EmergenciaRepository(db)
    emergencia = await repo.get(id_emergencia)
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada")
    
    # Solo el dueño puede editar
    if emergencia.idCliente != user_id:
         raise HTTPException(status_code=403, detail="No tienes permiso para editar esta emergencia")

    # Solo se puede editar si no ha sido aceptada (idEstado de PENDIENTE)
    estado_repo = EstadoRepository(db)
    estado_pend = await estado_repo.get_by_nombre("PENDIENTE")
    
    if not estado_pend or emergencia.idEstado != estado_pend.id:
        raise HTTPException(status_code=400, detail="No se puede editar una emergencia que ya está siendo atendida")

    # 2. Actualizar datos básicos
    update_data = {
        "descripcion": data.descripcion,
        "latitud": data.latitud,
        "longitud": data.longitud,
        "direccion": data.direccion,
        "audio_url": data.audio_url
    }
    
    await repo.update(db_obj=emergencia, obj_in=update_data)
    
    # 3. Re-procesar IA si hay contenido
    print(f"🔍 [Update] Evaluando IA: desc={bool(data.descripcion)}, texto_ad={bool(data.texto_adicional)}, fotos={len(data.evidencias_urls)}")
    if data.descripcion or data.texto_adicional or data.evidencias_urls:
        from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.services.ai_service import analizar_transcripcion_whisper
        from app.core.config import settings

        # Contexto del vehículo
        vehiculo_repo = VehiculoRepository(db)
        veh = await vehiculo_repo.get_by_placa(data.placaVehiculo)
        vehiculo_contexto = f"{veh.marca} {veh.modelo} ({veh.anio})" if veh else ""

        # Categorías y Prioridades activas
        categoria_repo = CategoriaProblemaRepository(db)
        prioridad_repo = PrioridadRepository(db)
        
        categorias = await categoria_repo.get_all()
        prioridades = await prioridad_repo.get_all()
        
        categorias_activas = [{"id": r.id, "nombre": r.descripcion} for r in categorias]
        prioridades_activas = [{"id": r.id, "nombre": r.descripcion} for r in prioridades]

        # Construir URLs completas
        base_url_simple = f"http://{settings.APP_HOST}:8000"
        full_urls = []
        for u in data.evidencias_urls:
            if u.startswith('http'):
                full_urls.append(u)
            elif u.startswith('uploads/'):
                full_urls.append(f"{base_url_simple}/{u}")
            else:
                full_urls.append(f"{base_url_simple}/uploads/{u}")

        # Combinar descripción y texto adicional para mejor contexto
        texto_para_ia = data.texto_adicional or data.descripcion or "Sin descripción"
        if data.texto_adicional and data.descripcion and data.texto_adicional != data.descripcion:
            texto_para_ia = f"{data.descripcion}. {data.texto_adicional}"

        print(f"🖼️ [Update] URLs enviadas a IA: {full_urls}")
        
        ia_result = await analizar_transcripcion_whisper(
            texto_crudo=texto_para_ia,
            vehiculo_info=vehiculo_contexto,
            categorias_disponibles=categorias_activas,
            prioridades_disponibles=prioridades_activas,
            evidencias_urls=full_urls
        )

        # 4. Actualizar Resumen IA
        resumen_repo = ResumenIARepository(db)
        resumen_ia = await resumen_repo.get_by_emergencia(id_emergencia)
        
        ficha_tecnica = ia_result.ficha_tecnica.model_dump() if ia_result.ficha_tecnica else {}
        resumen_taller = ia_result.resumen_taller

        if resumen_ia:
            await resumen_repo.update(db_obj=resumen_ia, obj_in={
                "resumen": resumen_taller,
                "ficha_tecnica": ficha_tecnica,
                "recomendaciones_taller": ia_result.recomendaciones_taller,
                "motivo_rechazo": ia_result.motivo_rechazo
            })
        else:
            await resumen_repo.create(obj_in={
                "resumen": resumen_taller,
                "ficha_tecnica": ficha_tecnica,
                "recomendaciones_taller": ia_result.recomendaciones_taller,
                "motivo_rechazo": ia_result.motivo_rechazo,
                "idEmergencia": emergencia.id
            })

        # Actualizar flags y clasificación
        await repo.update(db_obj=emergencia, obj_in={
            "es_valida": ia_result.es_valida,
            "idCategoria": ia_result.id_categoria,
            "idPrioridad": ia_result.id_prioridad 
        })

    # 5. Actualizar Evidencias (Borrar antiguas y poner nuevas)
    evidencia_repo = EvidenciaRepository(db)
    await evidencia_repo.delete_by_emergencia(id_emergencia)
    
    for url in data.evidencias_urls:
        await evidencia_repo.create(obj_in={
            "direccion": url,
            "idEmergencia": id_emergencia
        })

    await db.commit()
    await db.refresh(emergencia)
    return emergencia

async def cancelar_emergencia(id_emergencia: int, user_id: int, db: AsyncSession):
    repo = EmergenciaRepository(db)
    emergencia = await repo.get(id_emergencia)
    
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada")
    
    if emergencia.idCliente != user_id:
         raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta emergencia")

    if emergencia.idTaller is not None:
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar una emergencia que ya ha sido aceptada por un taller. Intente contactar con soporte."
        )

    await repo.delete(id_emergencia)
    await db.commit()
    
    return {"status": "success", "message": "Emergencia eliminada permanentemente"}

