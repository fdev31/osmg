# Module which can be replaced by webserver configuration to be statically served

from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse


def index_html():
    return RedirectResponse("/index.html")


async def roomsAccess(sessionId) -> RedirectResponse:
    "Redirects a nice /r/<session>/ url into the real one"
    return RedirectResponse("/join.html?session=" + sessionId)


def init(app, config):
    app.get("/r/{sessionId}")(roomsAccess)
    app.get("/", include_in_schema=False)(index_html)
    app.mount("/", StaticFiles(directory=config.static_dir), name="static")
