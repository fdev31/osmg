from back.models import newPlayer, Session
from back.sessionmanager import getSession
from back.globalHandlers import getRedis, getGameDataPrefix

async def dieAction(player: newPlayer, value: int) -> Session:
    redis = getRedis()
    prefix = getGameDataPrefix(newPlayer.sessionName, newPlayer.id)
    propName = "%s:g:diceValue"%(prefix)
    with redis.client() as conn:
        await conn.incrby(propName, value)
        await conn.get(propName)
        sess = await getSession(newPlayer.sessionName, conn)
    # TODO: update session + publish notification
    return sess

class DiceInterface:
    @staticmethod
    def getPlayerData():
        return dict(diceValue=2040)

    @staticmethod
    def getGameData():
        return {}

    actions = {
        'throwDice': dieAction,
        'validateDice': dieAction,
    }

definition = {'dice': DiceInterface}