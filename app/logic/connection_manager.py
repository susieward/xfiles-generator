import asyncio
import gc
from typing import Dict, Tuple
from fastapi import WebSocket
from app.logic.text_generator import TextGenerator

class ConnectionManager:
    def __init__(self, websocket: WebSocket, generator: TextGenerator):
        self.websocket = websocket
        self.generator = generator

    async def __aenter__(self):
        await self.websocket.accept()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        print('ConnectionManager: exit called:', exc_type, exc_value, traceback)
        try:
            await self.websocket.close()
        except Exception as e:
            print(e)
            pass
        finally:
            return True

    async def receive_json(self):
        async for message in self.websocket.iter_json():
            await self.handle_message(*self.parse_message(message))

    async def handle_message(self, start_string, max_length):
        print('starting generation...')
        try:
            generator = self.generator.generate(start_string, max_length)
            async for response in generator:
                await self.websocket.send_text(response)
                await asyncio.sleep(0.01)
        except Exception as e:
            print('handle_message:', e)
            raise e
        finally:
            print('generation done')
            gc.collect()

    def parse_message(self, data: Dict) -> Tuple:
        start_string = data.get('start_string')
        max_length = int(data.get('char_length'))
        #temperature = float(data.get('temp'))
        return start_string, max_length
