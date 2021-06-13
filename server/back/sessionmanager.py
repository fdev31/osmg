__all__ = ['getSession', 'registerGame']
import time
import logging
from typing import Dict, Any
import asyncio

import aioredis
from fastapi import HTTPException, BackgroundTasks
from starlette import status as httpstatus

from back.models import PlayerIdentifier, newPlayer, Session, RedisSession, getPropertieList
from back.models import SESSION_PLAYERS_DATA, SESSION_S_TIME, SESSION_GAME_TYPE
from back.models import SESSION_C_TIME, SESSION_GAME_DATA, SESSION_NAME, SESSION_PLAYERS
from back.globalHandlers import getGameDataPrefix, getRedis, setRedis, publishEvent, getSessionPrefix, getVarName
from back.globalHandlers import PLAYERS_READY, PLAYERS_ORDER

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

    async with (client or getRedis().client()) as conn:
        gameType  = await conn.get(getVarName(SESSION_GAME_TYPE, uid))
        vn = getVarName(PLAYERS_ORDER, uid, gameData=True)
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
    for field in (SESSION_C_TIME, SESSION_NAME, SESSION_GAME_TYPE):
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
        await conn.rpush(getVarName(PLAYERS_ORDER, player.sessionName, gameData=True), pid)
        await conn.mset(redisObj)
        await conn.incr(prefix+'nbPlayers')

        pub = publishEvent(player.sessionName, None, cat='newPlayer', name=player.name, avatar=player.avatar, id=pid)
        sess = await getSession(player.sessionName, conn)
        await pub

    sess.secret = secretId
    logger.debug(f"New player {pid}")
    return sess

async def startGame(player: PlayerIdentifier, tasks: BackgroundTasks) -> None:
    """ Notifies that some player is ready to start the game """
    redis = getRedis()
    g_prefix = getGameDataPrefix(player.sessionName)
    async with redis.client() as conn:
        pr = g_prefix + PLAYERS_READY
        if await conn.sismember(pr, player.id):
            raise HTTPException(httpstatus.HTTP_409_CONFLICT, "Action already done")
        await publishEvent(player.sessionName, conn, cat="ready", player=player.id)
        await conn.sadd(pr, player.id)
        await conn.set(f'S{player.sessionName}:'+SESSION_S_TIME, int(time.time()))

        async def checkStartOfGame():
            await asyncio.sleep(1)
            async with redis.client() as conn:
                nbPlayersReady = await conn.scard(pr)
                if int(nbPlayersReady) == int(await conn.get(getSessionPrefix(player.sessionName)+'nbPlayers')):
                    # all players are ready!
                    await publishEvent(player.sessionName, conn, cat="start", msg="game started")
                    gameType  = await getRedis().get(getVarName(SESSION_GAME_TYPE, player.sessionName))
                    await games[gameType].startGame(player.sessionName, conn)
        tasks.add_task(checkStartOfGame)

def init(app, config):
    setRedis(aioredis.from_url('redis://'+config.redis_server,  decode_responses=True))

    app.post('/session/new',
        response_model=Session)(makeSession)
    app.post('/session/join',
        responses={
            409: {'description': "player already joined"},
        },
        response_model=Session)(addPlayer)

    app.post('/session/start',
            response_model=None,
            responses={
                409: {"description": "player already exists"},
            })(startGame)
