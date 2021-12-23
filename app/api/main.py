import os
import asyncio
import signal
from fastapi import FastAPI
from app.api.routers import socket
from app.api.events import on_startup, on_shutdown
from app.config import get_config

def get_app():
    app = FastAPI()
    app.state.config = get_config()

    app.add_event_handler("startup", on_startup(app))
    app.add_event_handler("shutdown", on_shutdown(app))

    if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGQUIT, lambda _: asyncio.create_task(on_shutdown()))

    app.include_router(socket.router)
    return app

app = get_app()
