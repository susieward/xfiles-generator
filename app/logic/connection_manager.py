import asyncio
from typing import List
from fastapi import WebSocket
from starlette.websockets import WebSocketState
from app.logic.text_generator import TextGenerator

class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self._text_generator = TextGenerator()
        self._generate = None

    async def connect(self, websocket: WebSocket, client_id: str):
        if not self._text_generator.initialized:
            print('spinning up generator')
            await self._text_generator.initialize()
            self._generate = self._text_generator.generate
            print('generator online')
        await websocket.accept()
        self.connections.append(websocket)

    async def disconnect(self, websocket):
        print('disconnect called')
        self.connections.remove(websocket)
        print('number of connections: ', len(self.connections))

        if len(self.connections) == 0:
            print('shutting down generator')
            await self._text_generator.cleanup()
            self._generate = None
            print('shutdown complete. generator offline')

    async def receive_json(self, websocket):
        async for message in websocket.iter_json():
            await self.handle_message(websocket, message)

    async def handle_message(self, websocket, message):
        async for payload in self._generate(message):
            await websocket.send_text(payload)
            await asyncio.sleep(0)
