import logging
import aioredis
from typing import Dict, Any
from functools import lru_cache

from .utils import dumps

logger = logging.getLogger("redis")

ctx : Dict[str, Any] = {}

def getRedis() -> aioredis.Redis:
    return ctx['redis']

def setRedis(handler: aioredis.Redis):
    ctx['redis'] = handler

def publishEvent(topic, client=None, **params):
    logger.debug("PUBLISH %s %s", topic, params)
    return (client or ctx['redis']).publish(topic, dumps(params))

@lru_cache(128)
def _getVarPrefix(sessionId, playerId, gameData):
    if gameData and playerId:
        return f"S{sessionId}:{playerId}:g:"
    elif playerId:
        return f"S{sessionId}:{playerId}:"
    elif gameData:
        return f"S{sessionId}:g:"
    else:
        return f"S{sessionId}:"

def getVarName(name, sessionId, playerId=None, gameData=False):
    " get a REDIS key name from a variable + associated info "
    return _getVarPrefix(sessionId, playerId, gameData) + name

# deprecated functions:

def getGameDataPrefix(uid, playerId=None):
    if playerId:
        return 'S%s:%s:g:' % (uid, playerId)
    return 'S%s:g:'%(uid)

PLAYERS_READY = 'playersReady'
PLAYERS_ORDER = 'playerOrder'
PLAYERS_CONNECTED = 'playersOnline'
