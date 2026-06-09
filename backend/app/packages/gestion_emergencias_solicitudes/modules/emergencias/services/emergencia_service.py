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
import logging

logger = logging.getLogger(__name__)

from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.emergencia import Emergencia
from app.packages.gestion_usuarios_seguridad.modules.usuarios_vehiculos.models.vehiculo import Vehiculo
from app.packages.gestion_usuarios_seguridad.modules.tenants.models.taller import Taller
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.estado import Estado
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.emergencia_repo import EmergenciaRepository
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.schemas.emergencia import EmergenciaCreate, EmergenciaOut, ActualizarEstadoRequest
from app.core.config import settings

# Repositories
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.services.ai_service import analizar_transcripcion_whisper
from typing import List
import math
from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.services.notification_service import NotificationService

from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.categoria_problema import CategoriaProblema
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.prioridad import Prioridad
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.evidencia import Evidencia
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.models.historial_estado import HistorialEstado
from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.models.resumen_ia import ResumenIA
from app.packages.gestion_emergencias_solicitudes.modules.auxilio_solicitudes.models.asignacion_tecnico_emergencia import AsignacionTecnicoEmergencia
from app.packages.gestion_administrativa_reportes.modules.pagos.models.pago import Pago

# ─── CU04 ─────────────────────────────────────────────────────────

async def reportar_emergencia(
    data: EmergenciaCreate,
    cliente_id: int,
    db: AsyncSession,
) -> EmergenciaOut:
    import uuid
    # 1. Idempotencia: Verificar si ya existe una emergencia con este uuid_local
    if data.uuid_local:
        result = await db.execute(select(Emergencia).where(Emergencia.uuid_local == data.uuid_local))
        existente = result.scalar_one_or_none()
        if existente:
            print(f"[Offline Sync] Emergencia {data.uuid_local} ya estaba registrada. Devolviendo existente.")
            return await obtener_emergencia_detalle(existente.id, db)
    else:
        # Generar un UUID único en el backend si el cliente no lo envía
        data.uuid_local = str(uuid.uuid4())

    # Validar que el vehículo pertenece al cliente y obtener datos para la IA
    vehiculo = await Vehiculo.get_by_placa(db, data.placaVehiculo)
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
            
            categorias = await CategoriaProblema.get_all(db, )
            prioridades = await Prioridad.get_all(db, )
            
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
    emergencia = await Emergencia.create(db, obj_in={
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
        "uuid_local": data.uuid_local,
        "es_valida": True # Se actualizará abajo si la IA lo dice
    })
    await db.flush()

    # CU05: Crear pago inicial en 0 para evitar nulos (Modo Failsafe)
    await Pago.create(db, obj_in={
        "monto": 0.0,
        "monto_comision": 0.0,
        "cliente_id": cliente_id,
        "emergencia_id": emergencia.id,
        "estado": "PENDIENTE"
    })
    await db.flush()

    # Guardar Evidencias (Fotos)
    for url in data.evidencias_urls:
        await Evidencia.create(db, obj_in={
            "direccion": url,
            "idEmergencia": emergencia.id
        })
    await db.flush()

    # Guardar análisis IA si fue procesado
    if resumen_taller:
        await ResumenIA.create(db, obj_in={
            "resumen": resumen_taller,
            "ficha_tecnica": ficha_tecnica,
            "recomendaciones_taller": ia_result.recomendaciones_taller if 'ia_result' in locals() else None,
            "motivo_rechazo": ia_result.motivo_rechazo if 'ia_result' in locals() else None,
            "idEmergencia": emergencia.id
        })
        if 'ia_result' in locals():
            await emergencia.update(db, obj_in={"es_valida": ia_result.es_valida})
            
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
    estado = await Estado.get_by_nombre(db, "PENDIENTE")
    if estado is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Estado 'PENDIENTE' no encontrado en BD. Ejecute el seed inicial.",
        )

    await emergencia.update(db, obj_in={"idEstado": estado.id})
    await HistorialEstado.create(db, obj_in={
        "idEmergencia": emergencia.id,
        "idEstado": estado.id,
    })
    await db.commit()

    return await obtener_emergencia_detalle(emergencia.id, db)

async def obtener_emergencia_detalle(id: int, db: AsyncSession):
    emergencia = await Emergencia.get_detalle_by_id(db, id)
    if emergencia:
        _populate_dynamic_fields(emergencia)
    return emergencia

def _populate_dynamic_fields(e: Emergencia):
    """Calcula campos que no estn en la tabla base para el esquema de salida."""
    try:
        if hasattr(e, 'estado') and e.estado:
            e.estado_actual = e.estado.nombre
        else:
            e.estado_actual = "DESCONOCIDO"
    except Exception:
        e.estado_actual = "DESCONOCIDO"

    # 2. Mutex (is_locked)
    e.is_locked = False
    if e.locked_by and e.locked_at:
        diff = datetime.datetime.now() - e.locked_at
        if diff.total_seconds() < 120:
            e.is_locked = True


# ─── CU14 (cliente consulta sus emergencias) ──────────────────────

async def listar_emergencias_cliente(cliente_id: int, db: AsyncSession):
    emergencias = await Emergencia.get_by_cliente(db, cliente_id)
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
    emergencia = await Emergencia.get(db, emergencia_id)
    if not emergencia or emergencia.idTaller != taller_cod:
        print(f"DEBUG 404: emergencia_idTaller={getattr(emergencia, 'idTaller', None)} vs taller_cod={taller_cod}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergencia no encontrada o no asignada a este taller. (Taller: {getattr(emergencia, 'idTaller', None)}, Token: {taller_cod})",
        )

    # Verificar que el estado existe
    estado = None
    estado_map = {
        "EN_RUTA": "EN_RUTEO",
        "EN CAMINO": "EN_RUTEO",
        "ATENDIENDO": "ATENDIDO",
        "FINALIZAR": "FINALIZADO"
    }
    
    if getattr(data, "estado_nombre", None):
        nombre_req = data.estado_nombre.upper()
        nombre_mapped = estado_map.get(nombre_req, nombre_req)
        estado = await Estado.get_by_nombre(db, nombre_mapped)
        
        # Auto-crear si no existe (soluciona DBs desincronizadas en VPS)
        if estado is None:
            print(f"DEBUG 404: Creando estado faltante automáticamente: {nombre_mapped}")
            estado = Estado(nombre=nombre_mapped, descripcion=f"Estado {nombre_mapped}")
            db.add(estado)
            await db.flush()
            
    elif getattr(data, "idEstado", None) is not None:
        estado = await Estado.get(db, data.idEstado)

    if estado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estado no válido: {getattr(data, 'estado_nombre', None)} / {getattr(data, 'idEstado', None)}",
        )

    emergencia = await emergencia.update(db, obj_in={"idEstado": estado.id})
    nuevo_historial = await HistorialEstado.create(db, obj_in={
        "idEmergencia": emergencia_id,
        "idEstado": estado.id
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
    emergencias = await Emergencia.get_by_taller(db, taller_cod)
    for e in emergencias:
        _populate_dynamic_fields(e)
    return emergencias


async def rechazar_emergencia_taller(emergencia_id: int, taller_cod: str, db: AsyncSession):
    """
    El taller rechaza una emergencia. 
    Vuelve a estado PENDIENTE, cancela la cotización y notifica al cliente.
    """
    emergencia = await Emergencia.get(db, emergencia_id)
    if not emergencia or emergencia.idTaller != taller_cod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergencia no encontrada o no asignada a este taller."
        )

    # 1. Cancelar cotización aceptada
    from app.packages.gestion_emergencias_solicitudes.modules.cotizaciones.repositories.cotizacion_repo import CotizacionRepository
    repo_cot = CotizacionRepository(db)
    cotizacion = await repo_cot.get_by_emergencia_and_taller(emergencia_id, taller_cod)
    
    if cotizacion and cotizacion.estado == "ACEPTADA":
        await repo_cot.update(db_obj=cotizacion, obj_in={"estado": "RECHAZADA"})

    # 2. Reset Emergencia to PENDIENTE (o el ID correspondiente)
    estado_pendiente = await Estado.get_by_nombre(db, "PENDIENTE")
    nuevo_id_estado = estado_pendiente.id if estado_pendiente else 1

    await emergencia.update(db, obj_in={
        "idTaller": None,
        "idEstado": nuevo_id_estado
    })
    
    await HistorialEstado.create(db, obj_in={
        "idEmergencia": emergencia_id,
        "idEstado": nuevo_id_estado
    })
    await db.commit()

    # 3. Notificar al Cliente (WS y Push)
    try:
        from app.core.socket_manager import manager
        room_id = f"emergencia_{emergencia_id}"
        await manager.broadcast_to_room(room_id, {
            "type": "taller_rechazado",
            "message": "El taller ha rechazado la emergencia. La cotización fue cancelada y la emergencia vuelve a estar en búsqueda de taller."
        })
        
        await NotificationService.enviar_notificacion_usuario(
            db, 
            emergencia.idCliente, 
            "Taller canceló el servicio", 
            "El taller asignado no podrá atenderte. Por favor revisa otras cotizaciones.",
            {"emergencia_id": str(emergencia_id), "tipo": "taller_rechazado"}
        )
    except Exception as e:
        print(f"Error notifying rejection: {e}")

    return {"status": "ok", "message": "Emergencia rechazada exitosamente"}


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

async def listar_emergencias_disponibles(taller_cod: str, current_user: dict, db: AsyncSession):
    """
    Lista emergencias que:
    1. No tienen taller asignado (idTaller IS NULL)
    2. La sucursal (o taller) tiene la especialidad requerida por la categoria de la emergencia
    3. Están dentro de un radio de 40km de la sucursal (o taller)
    """
    from app.packages.gestion_usuarios_seguridad.modules.tenants.models.sucursal import Sucursal
    from sqlalchemy import select
    from sqlalchemy.orm import joinedload
    
    # 1. Obtener datos de ubicación y especialidades
    bases_coords = [] # Lista de (lat, lon) validas
    especialidades_validas = set()

    if current_user.get("role") == "admin_sucursal" and current_user.get("sucursal"):
        sucursal = await db.get(Sucursal, current_user["sucursal"], options=[joinedload(Sucursal.especialidades)])
        if sucursal:
            if sucursal.latitud and sucursal.longitud:
                bases_coords.append((sucursal.latitud, sucursal.longitud))
            for e in sucursal.especialidades:
                especialidades_validas.add(e.id_especialidad)
    else:
        # Nivel taller (todas las sucursales del taller + la matriz)
        taller = await Taller.get_with_especialidades(db, taller_cod)
        if taller:
            if taller.latitud and taller.longitud:
                bases_coords.append((taller.latitud, taller.longitud))
            
            # Especialidades a nivel de taller (legado) o agrupar de sucursales
            especialidades_validas.update([a.idEspecialidad for a in taller.asignaciones])
            
            stmt = select(Sucursal).where(Sucursal.id_taller == taller_cod).options(joinedload(Sucursal.especialidades))
            sucursales = (await db.execute(stmt)).unique().scalars().all()
            for s in sucursales:
                if s.latitud and s.longitud:
                    bases_coords.append((s.latitud, s.longitud))
                for e in s.especialidades:
                    especialidades_validas.add(e.id_especialidad)

    especialidades_list = list(especialidades_validas)    
    print(f"Radar - Bases Coords: {bases_coords}", flush=True)
    print(f"Radar - Especialidades del Taller (incluyendo sucursales): {especialidades_list}", flush=True)
    
    if not especialidades_list:
        logger.warning(f"Radar - El taller/sucursal NO TIENE ESPECIALIDADES asignadas. Devolviendo lista vacía por seguridad.")
        return []

    # 3. Buscar emergencias sin taller asignado y en estado PENDIENTE / INICIADA
    estados_validos = []
    estado_iniciada = await Estado.get_by_nombre(db, "INICIADA")
    estado_pendiente = await Estado.get_by_nombre(db, "PENDIENTE")
    
    if estado_iniciada: estados_validos.append(estado_iniciada.id)
    if estado_pendiente: estados_validos.append(estado_pendiente.id)
    
    if not estados_validos:
        estados_validos = [1, 2] # Fallback
        
    todas_disponibles = await EmergenciaRepository(db).get_disponibles_para_taller(especialidades_list, estados_validos)
    print(f"Radar - Emergencias encontradas en BD que coinciden con especialidades: {len(todas_disponibles)}", flush=True)

    # 4. Filtrar por distancia (10km - como requerido)
    cercanas = []
    for e in todas_disponibles:
        # Si la base de datos no tiene NINGUNA coordenada registrada para sucursales o taller, mostramos todo por defecto para que no se bloquee.
        if not bases_coords:
            _populate_dynamic_fields(e)
            cercanas.append(e)
            continue
            
        if not e.latitud or not e.longitud: 
            print(f"Radar - Ignorando emergencia {e.id} porque no tiene coordenadas (lat/lon).", flush=True)
            continue
            
        # Comprobar la menor distancia a CUALQUIER base (taller o sucursal)
        min_dist = float('inf')
        for lat_base, lon_base in bases_coords:
            dist = haversine_distance(lat_base, lon_base, e.latitud, e.longitud)
            if dist < min_dist:
                min_dist = dist
                
        print(f"Radar - Evaluando emergencia {e.id} a dist {min_dist:.2f} km de la base más cercana.", flush=True)
        if min_dist <= 10: # Radio de 10km estricto como pide el usuario
            _populate_dynamic_fields(e)
            cercanas.append(e)
        else:
            print(f"Radar - Descartando emergencia {e.id} por superar los 10km (distancia={min_dist:.2f}km)", flush=True)
            
    print(f"Radar - Emergencias finales enviadas al frontend: {len(cercanas)}", flush=True)
    return cercanas

async def bloquear_emergencia_temporal(emergencia_id: int, taller_cod: str, db: AsyncSession):
    """Establece un mutex temporal de 2 minutos."""
    emergencia = await Emergencia.get(db, emergencia_id)
    # Bloquear solo si no existe o si ya fue tomada por OTRO taller
    if not emergencia or (emergencia.idTaller and emergencia.idTaller != taller_cod):
        raise HTTPException(status_code=400, detail="Emergencia no disponible para análisis.")
    
    await emergencia.update(db, obj_in={
        "locked_by": taller_cod,
        "locked_at": datetime.datetime.now()
    })
    await db.commit()
    return {"status": "locked", "expires_in": 120}

async def asignar_emergencia_taller(emergencia_id: int, taller_cod: str, tecnicos_ids: list[int], db: AsyncSession, id_sucursal: int = None):
    """Asignación final con uno o varios técnicos."""
    # 1. Obtener emergencia
    emergencia = await Emergencia.get(db, emergencia_id)
    
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada.")
    
    if emergencia.idTaller and emergencia.idTaller != taller_cod:
        raise HTTPException(status_code=400, detail="Esta emergencia ya fue tomada por otro taller.")

    # 2. Realizar asignación
    await emergencia.update(db, obj_in={
        "idTaller": taller_cod,
        "idSucursal": id_sucursal,
        "locked_by": None,
        "locked_at": None
    })
    
    # 3. Registrar técnicos
    await AsignacionTecnicoEmergencia.delete_by_emergencia(db, emergencia_id)

    for t_id in tecnicos_ids:
        await AsignacionTecnicoEmergencia.create(db, obj_in={"idEmergencia": emergencia_id, "idTecnico": t_id})
    
    # 4. Actualizar estado a 'ASIGNADO'
    estado = await Estado.get_by_nombre(db, "ASIGNADO")
    
    nuevo_id_estado = estado.id if estado else 2
    await emergencia.update(db, obj_in={"idEstado": nuevo_id_estado})
    await HistorialEstado.create(db, obj_in={
        "idEmergencia": emergencia_id,
        "idEstado": nuevo_id_estado
    })
        
    await db.commit()
    # Refrescamos para tener los datos del objeto actualizados tras el commit
    await db.refresh(emergencia)

    # 5. NOTIFICACIÓN AL CLIENTE (CU12)
    try:
        taller = await Taller.get(db, taller_cod)
        
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

        # 6. Notificar a los técnicos asignados
        for t_id in tecnicos_ids:
            print(f"DEBUG: Notificando asignación al técnico {t_id}")
            await NotificationService.enviar_notificacion_usuario(
                db,
                t_id,
                "🚨 ¡Nueva Emergencia Asignada!",
                f"El taller '{taller.nombre}' te ha asignado una emergencia. Por favor, revisa la aplicación.",
                {
                    "emergencia_id": str(emergencia_id),
                    "tipo": "emergencia_asignada_tecnico"
                }
            )
        
        # [WS] Notificar asignación en tiempo real
        from app.core.socket_manager import manager
        room_id = f"emergencia_{emergencia_id}"
        await manager.broadcast_to_room(room_id, {
            "type": "taller_asignado",
            "taller_cod": taller_cod,
            "taller_nombre": taller.nombre,
            "distancia": dist_str,
            "tiempo": str(tiempo_estimado),
            "message": f"El taller '{taller.nombre}' ha sido asignado a tu emergencia."
        })
        
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
    emergencia = await Emergencia.get(db, emergencia_id)
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada.")
    if emergencia.idTaller != taller_cod:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta emergencia.")
    
    # Obtener o crear ResumenIA
    resumen = await ResumenIA.get_by_emergencia(db, emergencia_id)
    
    if resumen:
        # Actualizar ficha técnica existente (merge con datos nuevos)
        existing_ficha = resumen.ficha_tecnica or {}
        existing_ficha.update(data.get("ficha_tecnica", {}))
        
        update_data = {"ficha_tecnica": existing_ficha}
        if "resumen" in data:
            update_data["resumen"] = data["resumen"]
            
        await resumen.update(db, obj_in=update_data)
    else:
        # Crear resumen si no fue generado por IA
        await ResumenIA.create(db, obj_in={
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
        emergencia = await Emergencia.get_detalle_by_id(db, emergencia_id)
        
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
        if emergencia.pago:
            await emergencia.pago.update(db, obj_in={
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

            await Pago.create(db, obj_in={
                "monto": monto,
                "monto_comision": comision,
                "cliente_id": c_id,
                "emergencia_id": e_id,
                "estado": "PENDIENTE",
                "detalle_factura": factura
            })
            await db.flush()
        
        # Cambiar a estado ATENDIDO (ID 6 según check_states.py)
        await emergencia.update(db, obj_in={"idEstado": 6})
        await HistorialEstado.create(db, obj_in={
            "idEmergencia": emergencia_id,
            "idEstado": 6,
        })
        
        await db.commit()
        
        # 4. Notificar al Cliente
        try:
            await NotificationService.enviar_notificacion_usuario(
                db,
                emergencia.idCliente,
                "¡Trabajo Terminado! ",
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
    emergencia = await Emergencia.get(db, id_emergencia)
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada")
    
    # Solo el dueño puede editar
    if emergencia.idCliente != user_id:
         raise HTTPException(status_code=403, detail="No tienes permiso para editar esta emergencia")

    # Solo se puede editar si no ha sido aceptada (idEstado de PENDIENTE)
    estado_pend = await Estado.get_by_nombre(db, "PENDIENTE")
    
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
    
    await emergencia.update(db, obj_in=update_data)
    
    # 3. Re-procesar IA si hay contenido
    print(f"[Update] Evaluando IA: desc={bool(data.descripcion)}, texto_ad={bool(data.texto_adicional)}, fotos={len(data.evidencias_urls)}")
    if data.descripcion or data.texto_adicional or data.evidencias_urls:
        from app.packages.inteligencia_artificial_automatizacion.modules.motor_ia.services.ai_service import analizar_transcripcion_whisper
        from app.core.config import settings

        # Contexto del vehículo
        veh = await Vehiculo.get_by_placa(db, data.placaVehiculo)
        vehiculo_contexto = f"{veh.marca} {veh.modelo} ({veh.anio})" if veh else ""

        # Categorías y Prioridades activas
        
        categorias = await CategoriaProblema.get_all(db, )
        prioridades = await Prioridad.get_all(db, )
        
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

        print(f"[Update] URLs enviadas a IA: {full_urls}")
        
        ia_result = await analizar_transcripcion_whisper(
            texto_crudo=texto_para_ia,
            vehiculo_info=vehiculo_contexto,
            categorias_disponibles=categorias_activas,
            prioridades_disponibles=prioridades_activas,
            evidencias_urls=full_urls
        )

        # 4. Actualizar Resumen IA
        resumen_ia = await ResumenIA.get_by_emergencia(db, id_emergencia)
        
        ficha_tecnica = ia_result.ficha_tecnica.model_dump() if ia_result.ficha_tecnica else {}
        resumen_taller = ia_result.resumen_taller

        if resumen_ia:
            await resumen_ia.update(db, obj_in={
                "resumen": resumen_taller,
                "ficha_tecnica": ficha_tecnica,
                "recomendaciones_taller": ia_result.recomendaciones_taller,
                "motivo_rechazo": ia_result.motivo_rechazo
            })
        else:
            await ResumenIA.create(db, obj_in={
                "resumen": resumen_taller,
                "ficha_tecnica": ficha_tecnica,
                "recomendaciones_taller": ia_result.recomendaciones_taller,
                "motivo_rechazo": ia_result.motivo_rechazo,
                "idEmergencia": emergencia.id
            })

        # Actualizar flags y clasificación
        await emergencia.update(db, obj_in={
            "es_valida": ia_result.es_valida,
            "idCategoria": ia_result.id_categoria,
            "idPrioridad": ia_result.id_prioridad 
        })

    # 5. Actualizar Evidencias (Borrar antiguas y poner nuevas)
    await Evidencia.delete_by_emergencia(db, id_emergencia)
    
    for url in data.evidencias_urls:
        await Evidencia.create(db, obj_in={
            "direccion": url,
            "idEmergencia": id_emergencia
        })

    await db.commit()
    await db.refresh(emergencia)
    return emergencia

async def cancelar_emergencia(id_emergencia: int, user_id: int, db: AsyncSession):
    emergencia = await Emergencia.get(db, id_emergencia)
    
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada")
    
    if emergencia.idCliente != user_id:
         raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta emergencia")

    if emergencia.idTaller is not None:
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar una emergencia que ya ha sido aceptada por un taller. Intente contactar con soporte."
        )

    await Emergencia.delete(db, id_emergencia)
    await db.commit()
    
    return {"status": "success", "message": "Emergencia eliminada permanentemente"}

