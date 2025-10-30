from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/notification", tags=["notification"])


active_connections = []

@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def send_notification(message: str):
    for connection in active_connections:
        await connection.send_text(message)
