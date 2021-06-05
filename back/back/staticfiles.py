from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

async def roomsAccess(sessionId):
    return RedirectResponse('/static/join.html?session='+sessionId)

def init(app, config):
    app.mount("/static", StaticFiles(directory=config.static_dir), name="static")
    app.get("/r/{sessionId}")(roomsAccess)
