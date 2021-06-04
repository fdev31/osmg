from back.sessionmanager import getRedis, getSession, getGameDataPrefix, Session, newPlayer

async def dieAction(player: newPlayer, value: int):
    redis = getRedis()
    prefix = getGameDataPrefix(newPlayer.sessionName)
    propName = "%s_%s_dievalue"%(prefix, newPlayer.name)
    await redis.incrby(propName, value)
    await redis.get(propName)
    # TODO: update session + publish notification
    sess = await getSession(newPlayer.sessionName)
    return sess

def init(app, config):
    app.post('/game/die', response_model=Session)(dieAction)
