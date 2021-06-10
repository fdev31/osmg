from typing import Dict, Any
from back.utils import dumps

ctx : Dict[str, Any] = {}

def getRedis():
    return ctx['redis']

def setRedis(handler):
    ctx['redis'] = handler

def publishEvent(topic, client=None, **params):
    return (client or ctx['redis']).publish(topic, dumps(params))

def getSessionPrefix(uid):
    return 'S%s:'%uid

def getGameDataPrefix(uid, playerId=None):
    if playerId:
        return 'S%s:P%s:g:' % (uid, playerId)
    return 'S%s:g:'%(uid)
