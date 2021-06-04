import random

from fastapi.encoders import jsonable_encoder

from typing import Optional
from pydantic import BaseModel

"""
class Throw(BaseModel):
    faces: Optional[int] = 6
    count: Optional[int] = 1

def getDiceResuls(throw: Throw):
    return jsonable_encoder([random.randint(1, throw.faces) for i in range(throw.count)])
    """

def init(app, config):
    pass
    #app.post('/api/getDiceResults')(getDiceResuls)
