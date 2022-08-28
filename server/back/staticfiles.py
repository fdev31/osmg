# Module which can be replaced by webserver configuration to be statically served
import os

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from .utils import ODict

static_dir: str = ""


def index_html() -> Response:
    return RedirectResponse("/index.html")


async def roomsAccess(sessionId: str) -> FileResponse:
    "Redirects a nice /r/<session>/ url into the real one"
    return FileResponse(os.path.join(static_dir, "index.html"))


def init(app: FastAPI, config: ODict) -> None:
    global static_dir
    static_dir = config.static_dir
    app.get("/r/{sessionId}")(roomsAccess)
    app.get("/", include_in_schema=False)(index_html)
    app.mount("/", StaticFiles(directory=config.static_dir), name="static")
