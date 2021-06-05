from back.sessionmanager import getRedis, getSession, getGameDataPrefix, Session, newPlayer

async def dieAction(player: newPlayer, value: int):
    redis = getRedis()
    prefix = getGameDataPrefix(newPlayer.sessionName, newPlayer.id)
    propName = "%s:dievalue"%(prefix)
    with redis.client() as conn:
        await conn.incrby(propName, value)
        await conn.get(propName)
        sess = await getSession(newPlayer.sessionName, conn)
    # TODO: update session + publish notification
    return sess

def init(app, config):
    app.post('/game/die', response_model=Session)(dieAction)
