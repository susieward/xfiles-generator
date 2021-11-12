from fastapi import APIRouter, WebSocket, Depends
from app.logic.connection_manager import ConnectionManager
from app.logic.text_generator import TextGenerator
from app.api.dependencies import text_generator_dependency

router = APIRouter()

@router.websocket("/ws/{client_id}")
async def socket(
    websocket: WebSocket,
    client_id: str,
    text_generator: TextGenerator = Depends(text_generator_dependency)
):
    async with ConnectionManager(websocket=websocket, generator=text_generator) as conn:
        await conn.receive_json()
