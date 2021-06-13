import os
import importlib
import logging

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from .utils import ODict

debug = bool(os.environ.get('DEBUG', False))
logger = logging.getLogger()

logLevel = logging.DEBUG if debug else logging.WARNING

for name in 'access error'.split():
    l = logging.getLogger('uvicorn.'+name)
    l.propagate = False

logger.setLevel(logLevel)
logging.getLogger('uvicorn').setLevel(logLevel)
logging.getLogger('fastapi').setLevel(logLevel)
logging.getLogger('asyncio').setLevel(logLevel)

if debug:
    app = FastAPI(debug=True, default_response_class=ORJSONResponse)
else:
    app = FastAPI(debug=False, docs_url=None, redoc_url=None, default_response_class=ORJSONResponse)

config = ODict(
    static_dir=os.path.join(os.environ['PREFIX'], 'front'),
    redis_server=os.environ.get('REDIS_SERVER', 'localhost'),
    debug=debug,
)

# Load submodules

MODULES = 'staticfiles index sessionmanager stream games'.split()

if not debug:
    MODULES.pop(0)

for name in MODULES:
    logging.info("Loading %s ..." % name)
    mod = importlib.import_module('back.'+name)
    mod.init(app, config)
