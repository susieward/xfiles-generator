from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.logic.connection_manager import ConnectionManager

router = APIRouter()
connection_manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def socket(
    websocket: WebSocket,
    client_id: str
):
    await connection_manager.connect(websocket, client_id)
    while True:
        try:
            await connection_manager.receive_json(websocket)
        except Exception as e:
            print(e)
            await connection_manager.disconnect(websocket)
            break
