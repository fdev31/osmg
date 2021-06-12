__all__ = ['getSession', 'registerGame']
import time
import logging
from typing import Dict, Any
import hashlib

import aioredis
from fastapi import HTTPException
from starlette import status as httpstatus

from back.models import newPlayer, Session, Player
from back.globalHandlers import getRedis, setRedis, publishEvent, getSessionPrefix

logger = logging.getLogger("Session")
t0 = time.time()*1000
GAME_DATA = 'g'

async def _getUniquePlayerId():
    pid = await getRedis().incr('count_players')
    return pid

async def _genUniqueSessionId():
    pid = await getRedis().incr('count_session')
    return hex(int("%d%d"%(pid, (time.time()*1000)-t0)))[2:]

async def getSession(uid, client=None) -> Session:
    " fetch session info from redis "
    pattern = getSessionPrefix(uid) + "*"
    all_keys = []
    o = {}
    players : Dict[str, dict] = {}
    players_data : Dict[str, Any] = {}
    game_data = {}

    async with (client or getRedis().client()) as conn:
        cur = b"0"
        while cur:
            cur, keys = await conn.scan(cur, match=pattern)
            all_keys.extend((k for k in keys if ':_' not in k))

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

    o['players'] = list(players.values())
    o['playersData'] = players_data
    o['gameData'] = game_data
    return Session(**o)

games = {}

def registerGame(name, iface):
    games[name] = iface

def getPlayerInitialData(gameType):
    return games[gameType].getPlayerData().items()

def getGameInitialData(gameType):
    return games[gameType].getGameData().items()

# API handlers

async def makeSession() -> Session:
    " Create a new emtpy session with no players "
    uid = await _genUniqueSessionId()
    sess = Session(name = uid, players = [], creationTime=int(time.time()))

    prefix = getSessionPrefix(uid)

    props = {prefix+'nbPlayers': 0}

    for name, value in getGameInitialData(sess.gameType):
        props[f"{prefix}{GAME_DATA}:{name}"] = value
        sess.gameData[name] = value
    for field in ('creationTime', 'name', 'gameType'):
        props[prefix+field] = getattr(sess, field)

    await getRedis().mset(props)
    logger.debug(f"New session {uid}")
    return sess

async def connectPlayer(sessionName: str, playerId: str):
    await publishEvent(sessionName, None, cat='connectPlayer', id=playerId)

async def disconnectPlayer(sessionName: str, playerId: str):
    await publishEvent(sessionName, None, cat='disconnectPlayer', id=playerId)
    # TODO: mark as not ready
    # TODO: if no players anymore, remove the session

async def addPlayer(player: newPlayer) -> Session:
    " Add a player to an existing session "
    sess = await getSession(player.sessionName)

    for p in sess.players:
        if p['name'] == player.name:
            logger.debug(f"Attempt to create same player twice {player.name}")
            raise HTTPException(httpstatus.HTTP_409_CONFLICT, f"A player called {player.name} already exists")

    pidP = _getUniquePlayerId()
    player_info = player.dict()
    del player_info['sessionName']

    pid = await pidP
    secretId = int((time.time()*1000)%3600) + pid

    player_info['id'] = pid
    player_info['_secret'] = secretId

    redisObj = {}

    prefix = getSessionPrefix(player.sessionName)

    for name, value in player_info.items():
        redisObj[f"{prefix}P{pid}:{name}"] = value

    for name, value in getPlayerInitialData(sess.gameType):
        redisObj[f"{prefix}P{pid}:g:{name}"] = value

    async with getRedis().client() as conn:
        await conn.mset(redisObj)
        await conn.incr(prefix+'nbPlayers')

        pub = publishEvent(player.sessionName, None, cat='newPlayer', name=player.name, avatar=player.avatar, id=pid)
        sess = await getSession(player.sessionName, conn)
        await pub

    sess.secret = secretId
    logger.debug(f"New player {pid}")
    return sess

def init(app, config):
    setRedis(aioredis.from_url('redis://'+config.redis_server,  decode_responses=True))
    app.post('/session/new',
        response_model=Session)(makeSession)
    app.post('/session/join',
        responses={
            409: {'description': "player already joined"},
        },
        response_model=Session)(addPlayer)
