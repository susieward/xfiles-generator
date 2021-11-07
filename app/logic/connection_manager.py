import asyncio
from typing import List
from fastapi import WebSocket
from app.logic.text_generator import TextGenerator
from contextlib import AsyncExitStack

text_generator = TextGenerator()

class Connection:
    def __init__(self, websocket: WebSocket):
        self._websocket = websocket

    async def __aenter__(self):
        await self._websocket.accept()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        print('Connection: exit called:', exc_type, exc_value, traceback)
        try:
            await self._websocket.close()
        except Exception as e:
            print(e)
            pass
        finally:
            return True

    async def receive_json(self):
        async with text_generator as gen:
            async for message in self._websocket.iter_json():
                await self.handle_message(message, gen)

    async def handle_message(self, message, generator):
        print('starting generation...')
        try:
            output = generator.pipeline(message)
            generated = output[0]['generated_text']
            return await self._websocket.send_text(generated)
            #async for response in generator.generate(message):
                #await self._websocket.send_text(response)
                #await asyncio.sleep(0.02)
        except Exception as e:
            print('handle_message:', e)
            raise e
        finally:
            print('generation done')


class ConnectionManager(AsyncExitStack):
    def __init__(self):
        self.connections = set()
        super().__init__(self)

        #self._text_generator = TextGenerator()
        #self._generate = None

    async def __aenter__(self):
        self.push_async_callback(self.cancel_tasks, self.connections)
        super().__aenter__(self)

    async def __aexit__(self):
        print('exiting...')
        super().__aexit__(self)


    async def connect(self, websocket: WebSocket):
        conn = Connection(websocket=websocket)
        manager = conn.receive_json()
        messages = await stack.enter_async_context(manager)
        task = asyncio.create_task(conn.handle_messages(messages))
        self.connections.add(task)

    def disconnect(self, websocket):
        print('disconnect called')
        self.connections.remove(websocket)
        print('number of connections: ', len(self.connections))

    async def cancel_tasks(tasks):
        for task in tasks:
            if task.done():
                continue
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        #if len(self.connections) == 0:
        #    print('shutting down generator')
        #    await self._text_generator.cleanup()
        #    self._generate = None
        #    print('shutdown complete. generator offline')

    #async def receive_json(self, websocket):
    #    async for message in websocket.iter_json():
    #        await self.handle_message(websocket, message)


    #async def handle_message(self, websocket, message):
    #    gen = self._generate(message)
    #    while True:
    #        try:
    #            payload = await gen.__anext__()
    #            if payload is None:
    #                break
    #            await websocket.send_text(payload)
    #            await asyncio.sleep(0.04)
    #        except StopAsyncIteration:
    #            break
