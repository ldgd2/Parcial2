from sqlalchemy.ext.asyncio import AsyncSession
from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.schemas.chat import MensajeChatCreate
from app.core.socket_manager import manager
from fastapi import HTTPException

# Repositorios

async def enviar_mensaje(
    emergencia_id: int,
    data: MensajeChatCreate,
    remitente_id: int,
    rol: str,
    db: AsyncSession
):
    # 1. Verificar que la emergencia existe y su estado
    emergencia = await Emergencia.get(db, emergencia_id)
    
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada")

    if emergencia.idEstado in [7, 8]:
        raise HTTPException(status_code=403, detail="El chat ha finalizado para esta emergencia")

    # 2. Verificar propiedad/permiso del remitente
    if rol == "cliente":
        if emergencia.idCliente != remitente_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para este chat")
    elif rol in ["tecnico", "admin"]:
        if not emergencia.idTaller:
            raise HTTPException(status_code=403, detail="Esta emergencia aún no ha sido asignada a un taller")


        if rol == "tecnico":
            tecnico = await Tecnico.get(db, remitente_id)
            if not tecnico or tecnico.idTaller != emergencia.idTaller:
                raise HTTPException(status_code=403, detail="No perteneces al taller asignado")
        elif rol == "admin":
            taller = await Taller.get_by_admin(db, remitente_id)
            if not taller or taller.cod != emergencia.idTaller:
                raise HTTPException(status_code=403, detail="No eres el administrador del taller asignado")

    # 2. Guardar mensaje
    mensaje = await MensajeChat.create(db, obj_in={
        "idEmergencia": emergencia_id,
        "remitente_id": remitente_id,
        "rol_remitente": rol,
        "contenido": data.contenido,
        "imagen_url": data.imagen_url,
        "audio_url": data.audio_url
    })
    await db.flush()

    # 3. Notificar via WebSocket
    msg_dict = {
        "type": "chat_message",
        "id": mensaje.id,
        "idEmergencia": emergencia_id,
        "remitente_id": remitente_id,
        "rol_remitente": rol,
        "contenido": mensaje.contenido,
        "imagen_url": mensaje.imagen_url,
        "audio_url": mensaje.audio_url,
        "fecha_envio": mensaje.fecha_envio.isoformat()
    }

    # Enviar al cliente
    await manager.send_personal_message(msg_dict, str(emergencia.idCliente))
    
    # Enviar al taller (si está asignado)
    if emergencia.idTaller:
        await manager.send_personal_message(msg_dict, str(emergencia.idTaller))
        
        # También enviar al admin específico por si acaso
        taller = await Taller.get(db, emergencia.idTaller)
        if taller and taller.id_admin:
            await manager.send_personal_message(msg_dict, str(taller.id_admin))
    
    if rol != "cliente":
        # --- Notificación Push al Cliente (Móvil) ---

        from app.packages.inteligencia_artificial_automatizacion.modules.notificaciones.services.notification_service import NotificationService
        taller = await Taller.get(db, emergencia.idTaller)
        nombre_taller = taller.nombre if taller else "Taller Mecánico"
        
        cuerpo = data.contenido if data.contenido else "Foto recibida"
        
        await NotificationService.enviar_notificacion_usuario(
            db=db,
            user_id=emergencia.idCliente,
            titulo=nombre_taller,
            cuerpo=cuerpo,
            data={
                "emergencia_id": emergencia_id,
                "tipo": "chat"
            }
        )

    await db.commit()
    await db.refresh(mensaje)
    return mensaje

async def obtener_historial(emergencia_id: int, db: AsyncSession):
    return await MensajeChat.get_historial_por_emergencia(db, emergencia_id)
