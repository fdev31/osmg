import os
import importlib
import logging

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from .utils import ODict

debug = bool(os.environ.get("DEBUG", False))
logger = logging.getLogger("routes")

if debug:
    app = FastAPI(debug=True, default_response_class=ORJSONResponse)
else:
    app = FastAPI(
        debug=False,
        docs_url=None,
        redoc_url=None,
        default_response_class=ORJSONResponse,
    )

config = ODict(
    static_dir=os.path.join(os.environ.get("PREFIX", os.getcwd()), "front"),
    redis_server=os.environ.get("REDIS_SERVER", "localhost"),
    debug=debug,
)

# Load submodules

MODULES = "sessionmanager stream games".split()

if debug:
    MODULES.append("debug")
    MODULES.append("staticfiles")

for name in MODULES:
    logger.info("Loading %s ..." % name)
    mod = importlib.import_module("." + name, package="back")
    mod.init(app, config)
logger.info("Routes Loaded.")
