from fastapi.responses import RedirectResponse

def index_html():
    return RedirectResponse('/static/index.html')

def init(app, config):
    app.get("/")(index_html)
