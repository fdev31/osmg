import logging
import asyncio
from typing import Dict, Any

from ..models import Session, RedisSession, getPropertieList
from ..models import SESSION_PLAYERS_DATA, SESSION_S_TIME, SESSION_GAME_TYPE
from ..models import SESSION_GAME_DATA, SESSION_NAME, SESSION_PLAYERS
from ..globalHandlers import getRedis, getVarName
from ..globalHandlers import PLAYERS_ORDER, PLAYERS_CONNECTED
from ..globalHandlers import getRedis, publishEvent, getVarName

from .base import removeSession
from .library import games
from ..gamelib.interfaces import GameInterface

logger = logging.getLogger("Session")

GAME_DATA = 'g'

async def getGameBySessionId(uid: str, conn) -> GameInterface:
    gameType = await conn.get(getVarName(SESSION_GAME_TYPE, uid))
    return games[gameType]

async def isPlayerValid(conn, sessionId, playerId, secret):
    actualSecret = await conn.get(getVarName("_secret", sessionId, playerId))
    return int(actualSecret) == int(secret)

async def connectPlayer(sessionName: str, playerId: str):
    stage = getVarName(PLAYERS_CONNECTED+'stage', sessionName)
    async with getRedis().client() as conn:
        if await conn.sismember(stage, playerId):
            await conn.smove(stage, getVarName(PLAYERS_CONNECTED, sessionName), playerId)
        else:
            await conn.sadd(getVarName(PLAYERS_CONNECTED, sessionName), playerId)
            await publishEvent(sessionName, conn, cat='connectPlayer', id=playerId)

async def disconnectPlayer(sessionName: str, playerId: str):
    pr = getVarName(PLAYERS_CONNECTED, sessionName)
    stage = getVarName(PLAYERS_CONNECTED+'stage', sessionName)
    async with getRedis().client() as conn:
        await conn.smove(pr, stage, playerId)
        await asyncio.sleep(2)
        if not await conn.sismember(pr, playerId): # it has reconnected in the meantime
            await conn.srem(stage, playerId)
            nbP = await conn.scard(pr)
            if nbP == 0:
                await removeSession(sessionName, conn)
            else:
                await publishEvent(sessionName, conn, cat='disconnectPlayer', id=playerId)

async def getSession(uid, client=None) -> Session:
    " fetch session info from redis "

    async with (client or getRedis().client()) as conn:
        gameType  = await conn.get(getVarName(SESSION_GAME_TYPE, uid))
        vn = getVarName(PLAYERS_ORDER, uid)
        allPlayers = await conn.lrange(vn, 0, -1)

    iface = games[gameType]
    all_keys = [getVarName(name, uid) for name in getPropertieList(RedisSession)]
    all_keys.extend(getVarName(name, uid, gameData=True) for name in iface.getGameData().keys())

    playerDataKeys = list(iface.getPlayerData().keys())
    for playername in allPlayers:
        all_keys.extend(getVarName(name, uid, playername, gameData=True) for name in playerDataKeys)
        all_keys.extend(getVarName(name, uid, playername) for name in iface.getPlayerIdentifiers())

    o = {}
    players : Dict[str, dict] = {}
    players_data : Dict[str, Any] = {}
    game_data = {}

    async with (client or getRedis().client()) as conn:
        all_values = await conn.mget(all_keys)

    for key, val in zip(all_keys, all_values):
        splitk = key.split(':')
        if len(splitk) == 2:
            o[splitk[1]] = val
        elif splitk[1] == GAME_DATA:
            game_data[splitk[2]] = val
        else: # players
            if splitk[1] not in players:
                players[splitk[1]] = {}
                players_data[splitk[1]] = {}
            if splitk[2] == GAME_DATA: # players data
                players_data[splitk[1]][splitk[3]] = val
            else:
                players[splitk[1]][splitk[2]] = val

    o[SESSION_PLAYERS] = list(players.values())
    o[SESSION_PLAYERS_DATA] = players_data
    o[SESSION_GAME_DATA] = game_data
    o[SESSION_NAME] = uid
    if o[SESSION_S_TIME] is None:
        o[SESSION_S_TIME] = 0
    return Session(**o)
