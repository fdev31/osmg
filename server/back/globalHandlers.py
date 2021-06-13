from typing import Dict, Any
from back.utils import dumps

ctx : Dict[str, Any] = {}

def getRedis():
    return ctx['redis']

def setRedis(handler):
    ctx['redis'] = handler

def publishEvent(topic, client=None, **params):
    return (client or ctx['redis']).publish(topic, dumps(params))

def getVarName(name, sessionId, playerId=None, gameData=False):
    if gameData and playerId:
        return f"S{sessionId}:P{playerId}:g:{name}"
    elif playerId:
        return f"S{sessionId}:P{playerId}:{name}"
    elif gameData:
        return f"S{sessionId}:g:{name}"
    else:
        return f"S{sessionId}:{name}"

# deprecated functions:

def getGameDataPrefix(uid, playerId=None):
    if playerId:
        return 'S%s:P%s:g:' % (uid, playerId)
    return 'S%s:g:'%(uid)

PLAYERS_READY = 'playersReady'
PLAYERS_ORDER = 'playerOrder'
PLAYERS_CONNECTED = 'playersOnline'
