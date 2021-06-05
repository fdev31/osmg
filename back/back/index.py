from fastapi.responses import RedirectResponse

def index_html():
    return RedirectResponse('/static/index.html')

def favicon():
    return RedirectResponse('/static/favicon.ico')

def init(app, config):
    app.get("/")(index_html)
    app.get("/favicon.ico")(favicon)
