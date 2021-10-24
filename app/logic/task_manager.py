import asyncio
from contextlib import AsyncExitStack
from app.logic.connection_manager import ConnectionManager

async def start():
    async with AsyncExitStack() as stack:
        tasks = set()
        stack.push_async_callback(cancel_tasks, tasks)

        client = ConnectionManager()
        await stack.enter_async_context(client)

        connections = client.connections

        for connection in connections:
            manager = client.receive_json(connection)
            messages = await stack.enter_async_context(manager)
            task = asyncio.create_task(handle_messages(messages, client, connection))
            tasks.add(task)

        # Wait for everything to complete (or fail)
        await asyncio.gather(*tasks)


async def handle_messages(messages, client, connection):
    async for message in messages:
        await client.handle_message(connection, message)
        #print(message.payload.decode('utf-8'))

async def cancel_tasks(tasks):
    for task in tasks:
        if task.done():
            continue
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

async def main():
    reconnect_interval = 3
    while True:
        try:
            await start()
        except Exception as error:
            print(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
        finally:
            await asyncio.sleep(reconnect_interval)


#asyncio.run(main())
