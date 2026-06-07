import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.socket_manager import manager
from app.db.session import get_db
from app.packages.gestion_emergencias_solicitudes.modules.emergencias.repositories.emergencia_repo import EmergenciaRepository

# Implementación de Haversine para ETA si se usa cálculo básico en el backend
import math

def calculate_distance_km(lat1, lon1, lat2, lon2):
    R = 6371.0 # Radio de la Tierra en km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

router = APIRouter(tags=["Real-time — Auxilio"])

@router.websocket("/ws/auxilio/{emergencia_id}")
async def auxilio_websocket_endpoint(
    websocket: WebSocket,
    emergencia_id: int,
    user_id: str = Query(...), # En un caso real se usa un JWT token para verificar la identidad
    role: str = Query("cliente")
):
    await websocket.accept()
    room_id = f"emergencia_{emergencia_id}"
    
    # 1. Unirse a la sala de esta emergencia
    await manager.join_room(websocket, room_id)
    logging.info(f"[WS] Usuario {user_id} ({role}) se unió a la sala {room_id}")

    try:
        while True:
            # Recibir datos JSON
            data_str = await websocket.receive_text()
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                continue
            
            event_type = data.get("type")
            
            if event_type == "gps" and role == "tecnico":
                # El técnico envía su posición. Calculamos el ETA en el backend
                lat_tec = data.get("lat")
                lng_tec = data.get("lng")
                lat_cli = data.get("dest_lat")
                lng_cli = data.get("dest_lng")
                
                eta_str = "Desconocido"
                if lat_tec and lng_tec and lat_cli and lng_cli:
                    dist_km = calculate_distance_km(float(lat_tec), float(lng_tec), float(lat_cli), float(lng_cli))
                    # Asumiendo una velocidad promedio en ciudad de 30 km/h
                    tiempo_horas = dist_km / 30.0
                    tiempo_minutos = max(1, int(tiempo_horas * 60))
                    eta_str = f"{tiempo_minutos} min"

                broadcast_data = {
                    "type": "gps_update",
                    "lat": lat_tec,
                    "lng": lng_tec,
                    "eta": eta_str,
                    "distance_km": round(dist_km, 2) if lat_cli else 0
                }
                
                # Reenviar al cliente (a todos menos al emisor)
                await manager.broadcast_to_room(room_id, broadcast_data, exclude=websocket)

            elif event_type == "chat":
                # Mensaje de chat efímero
                texto = data.get("text")
                sender = data.get("sender_name", user_id)
                broadcast_data = {
                    "type": "chat_message",
                    "text": texto,
                    "sender_role": role,
                    "sender_name": sender
                }
                await manager.broadcast_to_room(room_id, broadcast_data, exclude=websocket)

            elif event_type == "repair_update" and role == "tecnico":
                # Notificación en tiempo real de lo que hace el técnico en el sitio
                texto_reparacion = data.get("text", "Actualizando estado de la reparación...")
                broadcast_data = {
                    "type": "repair_update",
                    "text": texto_reparacion,
                    "timestamp": data.get("timestamp", "")
                }
                await manager.broadcast_to_room(room_id, broadcast_data, exclude=websocket)

    except WebSocketDisconnect:
        manager.leave_room(websocket, room_id)
        logging.info(f"[WS] Usuario {user_id} ({role}) salió de la sala {room_id}")
