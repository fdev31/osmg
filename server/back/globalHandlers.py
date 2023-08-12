import logging
from functools import lru_cache
from typing import Any, Awaitable, Optional

import redis

from .utils import ODict, dumps

logger = logging.getLogger("redis")


class Context:
    config: ODict = ODict()
    redis: redis.Redis


def setConfig(config: ODict) -> None:
    Context.config = config


def getConfig() -> ODict:
    return Context.config


def getRedis() -> redis.Redis:
    return Context.redis


def getNewRedis() -> redis.Redis:
    return redis.from_url("redis://" + getConfig().redis_server, decode_responses=True)


def setRedis(handler: redis.Redis) -> None:
    Context.redis = handler


def publishEvent(
    topic: str,
    client: Optional[redis.Redis] = None,
    rcpt: str | None = None,
    **params: Any,
) -> Awaitable[int]:
    logger.debug("PUBLISH %s %s", topic, params)
    if rcpt:
        topic = topic + ":" + rcpt
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
