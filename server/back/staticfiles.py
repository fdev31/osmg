# Module which can be replaced by webserver configuration to be statically served

from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

def index_html():
    return RedirectResponse('/static/index.html')

def favicon():
    return RedirectResponse('/static/favicon.ico')

async def roomsAccess(sessionId) -> RedirectResponse:
    " Redirects a nice /r/<session>/ url into the real one "
    return RedirectResponse('/static/join.html?session='+sessionId)

def init(app, config):
    app.mount("/static", StaticFiles(directory=config.static_dir), name="static")
    app.get("/r/{sessionId}")(roomsAccess)
    app.get("/")(index_html)
    app.get("/favicon.ico")(favicon)
