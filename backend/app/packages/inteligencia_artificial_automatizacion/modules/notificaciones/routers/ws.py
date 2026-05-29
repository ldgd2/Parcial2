from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.socket_manager import manager

router = APIRouter(tags=["Real-time — WebSockets"])

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Mantener la conexión abierta y esperar mensajes (si fuera necesario)
            data = await websocket.receive_text()
            # Podríamos procesar mensajes entrantes aquí si fuera necesario
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
