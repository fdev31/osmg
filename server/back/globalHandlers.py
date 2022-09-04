import logging
from functools import lru_cache
from typing import Any, Awaitable, Optional

import aioredis

from .utils import ODict, dumps

logger = logging.getLogger("redis")


class Context:
    config: ODict = ODict()
    redis: aioredis.Redis


def setConfig(config: ODict) -> None:
    Context.config = config


def getConfig() -> ODict:
    return Context.config


def getRedis() -> aioredis.Redis:
    return Context.redis


def getNewRedis() -> aioredis.Redis:
    return aioredis.from_url(
        "redis://" + getConfig().redis_server, decode_responses=True
    )


def setRedis(handler: aioredis.Redis) -> None:
    Context.redis = handler


def publishEvent(
    topic: str, client: Optional[aioredis.Redis] = None, **params: Any
) -> Awaitable[int]:
    logger.debug("PUBLISH %s %s", topic, params)
    return (client or Context.redis).publish(topic, dumps(params))


@lru_cache(128)
def _getVarPrefix(sessionId: str, playerId: str, gameData: bool) -> str:
    if gameData and playerId:
        return f"S{sessionId}:{playerId}:g:"
    elif playerId:
        return f"S{sessionId}:{playerId}:"
    elif gameData:
        return f"S{sessionId}:g:"
    else:
        return f"S{sessionId}:"


def getVarName(
    name: str,
    sessionId: str,
    playerId: Optional[str] = None,
    gameData: Optional[bool] = False,
) -> str:
    "get a REDIS key name from a variable + associated info"
    return _getVarPrefix(sessionId, playerId, gameData) + name


@lru_cache(128)
def getGameVar(name: str, sessionId: str) -> str:
    return f"S{sessionId}:g:{name}"


@lru_cache(128)
def getSessionVar(name: str, sessionId: str) -> str:
    return f"S{sessionId}:{name}"


@lru_cache(128)
def getPlayerGameVar(name: str, sessionId: str, playerId: str) -> str:
    return f"S{sessionId}:{playerId}:g:{name}"


@lru_cache(128)
def getPlayerVar(name: str, sessionId: str, playerId: str) -> str:
    return f"S{sessionId}:{playerId}:{name}"


# deprecated functions:


def getGameDataPrefix(uid: str | int, playerId: Optional[str | int] = None) -> str:
    if playerId:
        return "S%s:%s:g:" % (uid, playerId)
    return "S%s:g:" % (uid)
