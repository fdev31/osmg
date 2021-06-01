import os
import sys
from fastapi import FastAPI

app = FastAPI()

class ODict(dict):
    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)

config = ODict(
        static_dir=os.environ['PREFIX'],
        )

# Load submodules

# Serve static files under /static (XXX: use nginx for production)
from back import staticfiles
staticfiles.init(app, config)

from back import index
index.init(app, config)

from back import api
api.init(app, config)
