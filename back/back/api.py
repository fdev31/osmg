import random

from fastapi.encoders import jsonable_encoder


def getDiceResuls(count: int=1, faces: int = 6):
    data = jsonable_encoder([random.randint(1, faces+1) for i in range(count)])
    return data

def init(app, config):
    app.get('/api/getDiceResults')(getDiceResuls)
