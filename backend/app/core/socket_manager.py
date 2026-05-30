from fastapi import WebSocket
from typing import Dict, List, Any
import json

class ConnectionManager:
    def __init__(self):
        # Almacena conexiones por ID de usuario o rol
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Almacena conexiones por Sala (Room)
        self.active_rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)

    def disconnect(self, websocket: WebSocket, client_id: str):
        if client_id in self.active_connections:
            if websocket in self.active_connections[client_id]:
                self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]

    async def join_room(self, websocket: WebSocket, room_id: str):
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = []
        if websocket not in self.active_rooms[room_id]:
            self.active_rooms[room_id].append(websocket)

    def leave_room(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_rooms:
            if websocket in self.active_rooms[room_id]:
                self.active_rooms[room_id].remove(websocket)
            if not self.active_rooms[room_id]:
                del self.active_rooms[room_id]

    async def broadcast_to_room(self, room_id: str, message: Any, exclude: WebSocket = None):
        if room_id in self.active_rooms:
            # Creamos una copia para evitar errores si la lista cambia durante la iteración
            for connection in list(self.active_rooms[room_id]):
                if connection != exclude:
                    try:
                        await connection.send_text(json.dumps(message))
                    except Exception:
                        pass

    async def send_personal_message(self, message: Any, client_id: str):
        if client_id in self.active_connections:
            for connection in list(self.active_connections[client_id]):
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    pass

    async def broadcast(self, message: Any):
        for connections in self.active_connections.values():
            for connection in list(connections):
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    pass

manager = ConnectionManager()
