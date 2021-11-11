import asyncio
import gc
from typing import List
from fastapi import WebSocket
from app.logic.text_generator import TextGenerator
from contextlib import AsyncExitStack


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

    async def receive_json(self, use_pipeline = False):
        async for message in self.websocket.iter_json():
            await self.handle_message(message, use_pipeline)

    async def handle_message(self, message, use_pipeline = False):
        print('starting generation...')
        try:
            if use_pipeline:
                response = self.generator.pipeline(message)
                text = response[0]['generated_text']
                return await self.websocket.send_text(text)
            else:
                async for response in self.generator.generate(message):
                    await self.websocket.send_text(response)
                    await asyncio.sleep(0.04)
        except Exception as e:
            print('handle_message:', e)
            raise e
        finally:
            print('generation done')
            gc.collect()
