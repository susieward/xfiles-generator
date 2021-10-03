import asyncio
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from app.api.exceptions import ConnectionException, TextGeneratorException

class ConnectionManager:
    def __init__(self, websocket: WebSocket, on_receive, client_id):
        self.websocket = websocket
        self._on_receive = on_receive
        self._client_id = client_id

    async def __aenter__(self):
        await self.websocket.accept()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        print('exit called: ', exc_type, str(exc_value), traceback)
        try:
            await self.websocket.close()
        except Exception as e:
            print(e)
            pass
        finally:
           return True

    async def receive_json(self):
        async for message in self.websocket.iter_json():
            await self.handle_message(message)

    async def handle_message(self, message):
        gen = self._on_receive(message)
        while True:
            try:
                await asyncio.sleep(0)
                payload = await gen.__anext__()
                if payload is None:
                    break
                await self.websocket.send_text(payload)
            except StopAsyncIteration:
                break
