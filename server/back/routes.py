import importlib
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from .utils import ODict

debug = bool(os.environ.get("DEBUG", False))
logger = logging.getLogger("routes")
logger.info(f"DEBUG: {debug}")

if debug:
    app = FastAPI(debug=True, default_response_class=ORJSONResponse)
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )
else:
    app = FastAPI(
        debug=False,
        docs_url=None,
        redoc_url=None,
        default_response_class=ORJSONResponse,
    )

config = ODict(
    static_dir=os.environ.get("FRONT_FILES", os.getcwd()),
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
