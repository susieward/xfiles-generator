from fastapi import APIRouter, WebSocket, Depends
from app.logic.connection_manager import Connection

router = APIRouter()

@router.websocket("/ws/{client_id}")
async def socket(
    websocket: WebSocket,
    client_id: str
):
    async with Connection(websocket=websocket) as conn:
        await conn.receive_json()
