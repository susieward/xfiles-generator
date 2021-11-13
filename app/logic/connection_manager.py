import asyncio
import gc
from typing import List, Dict
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
        print('Connection: exit called:', exc_type, exc_value, traceback)
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
        start_string, max_length, use_sync = self.parse_message(message)
        print('starting generation...')
        try:
            if use_sync:
                await self.websocket.send_text('Generating a lot of text, please wait...')
                await asyncio.sleep(0)
                response = await self.generator.generate_sync(start_string, max_length)
                return await self.websocket.send_text(response)
            else:
                async for response in self.generator.generate(start_string, max_length):
                    await self.websocket.send_text(response)
                    await asyncio.sleep(0.04)
        except Exception as e:
            print('handle_message:', e)
            raise e
        finally:
            print('generation done')
            gc.collect()

    def parse_message(self, data: Dict):
        start_string = data.get('start_string')
        max_length = int(data.get('char_length'))
        use_sync = bool(data.get('sync'))
        #temperature = float(data.get('temp'))
        return start_string, max_length, use_sync
