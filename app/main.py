from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from app.api.routers import base, socket
from app.api.events import init_char_lookup

def get_app():
    app = FastAPI()
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.mount("/static", StaticFiles(directory = "app/static"), name = "static")

    app.add_event_handler("startup", init_char_lookup(app))

    app.include_router(base.router)
    app.include_router(socket.router)
    return app

app = get_app()