import os
import sys
from fastapi import FastAPI

from .utils import ODict

app = FastAPI(debug=bool(os.environ.get('DEBUG', False)))

config = ODict(
        static_dir=os.path.join(os.environ['PREFIX'], 'front'),
        redis_server=os.environ.get('REDIS_SERVER', 'localhost'),
        )

# Load submodules

# Serve static files under /static (TODO: use nginx for production)
from back import staticfiles
staticfiles.init(app, config)

from back import index
index.init(app, config)

from back import sessionmanager
sessionmanager.init(app, config)

from back import games
games.init(app, config)
