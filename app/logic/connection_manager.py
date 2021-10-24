import asyncio
from typing import List
from fastapi import WebSocket
from starlette.websockets import WebSocketState
from app.logic.text_generator import TextGenerator

class ConnectionManager:
    def __init__(self, generator: TextGenerator):
        self.connections: List[WebSocket] = []
        self._text_generator = generator
        self._generate = self._text_generator.generate

    async def startup(self):
        if not self._text_generator.initialized:
           print('spinning up generator')
           await self._text_generator.initialize()
           self._generate = self._text_generator.generate
           print('generator online')
        return self

    async def shutdown(self):
        #print('exit called:', exc_type, exc_value, traceback)
        try:
            if len(self.connections) > 0:
                for connection in self.connections:
                    self.disconnect(connection)
            if self._text_generator.initialized:
                print('shutting down generator')
                await self._text_generator.cleanup()
                self._generate = None
                print('shutdown complete. generator offline')
        except Exception as e:
            print(e)
            pass
        finally:
            return True


    async def connect(self, websocket: WebSocket, client_id: str):
        #if not self._text_generator.initialized:
        #    print('spinning up generator')
        #    await self._text_generator.initialize()
        #    self._generate = self._text_generator.generate
        #    print('generator online')
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket):
        print('disconnect called')
        self.connections.remove(websocket)
        print('number of connections: ', len(self.connections))

        #if len(self.connections) == 0:
        #    print('shutting down generator')
        #    await self._text_generator.cleanup()
        #    self._generate = None
        #    print('shutdown complete. generator offline')

    async def receive_json(self, websocket):
        async for message in websocket.iter_json():
            await self.handle_message(websocket, message)


    async def handle_message(self, websocket, message):
        gen = self._generate(message)
        while True:
            try:
                payload = await gen.__anext__()
                if payload is None:
                    break
                await websocket.send_text(payload)
                await asyncio.sleep(0.04)
            except StopAsyncIteration:
                break
