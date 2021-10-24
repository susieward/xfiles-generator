from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.logic.connection_manager import ConnectionManager
from app.logic.text_generator import TextGenerator
from app.api.dependencies import get_manager

router = APIRouter()

@router.websocket("/ws/{client_id}")
async def socket(
    websocket: WebSocket,
    client_id: str,
    connection_manager: ConnectionManager = Depends(get_manager)
):
    await connection_manager.connect(websocket, client_id)
    try:
        await connection_manager.receive_json(websocket)
    except Exception as e:
        print(e)
        connection_manager.disconnect(websocket)
