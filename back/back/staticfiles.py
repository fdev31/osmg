from fastapi.staticfiles import StaticFiles

def init(app, config):
    app.mount("/static", StaticFiles(directory=config.static_dir), name="static")
