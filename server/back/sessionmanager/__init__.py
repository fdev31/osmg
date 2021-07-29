import time
import logging
import asyncio

import aioredis
from fastapi import HTTPException, BackgroundTasks
from starlette import status as httpstatus

from ..models import PlayerIdentifier, newPlayer, Session
from ..models import SESSION_PLAYERS_DATA, SESSION_S_TIME, SESSION_GAME_TYPE
from ..models import SESSION_C_TIME, SESSION_NAME, SESSION_PLAYERS

from ..globalHandlers import getRedis, setRedis, publishEvent, getVarName
from ..globalHandlers import PLAYERS_READY, PLAYERS_ORDER

from .base import genUniqueSessionId, getUniquePlayerId
from .library import games, getGameInitialData, getPlayerInitialData
from .public import getSession
from .votesystem import vote

logger = logging.getLogger("Session")


async def _triggerGameStart(game, uid, conn):
    await publishEvent(uid, conn, cat="start", msg="game started")
    await game.startGame(uid, conn)


async def makeSession() -> Session:
    "Create a new emtpy session with no players"
    uid = await genUniqueSessionId()
    sess = Session(name=uid, players=[], creationTime=int(time.time()))
    props = {}

    for name, value in getGameInitialData(sess.gameType):
        props[getVarName(name, sess.name, gameData=True)] = value
        sess.gameData[name] = value

    for field in (SESSION_C_TIME, SESSION_NAME, SESSION_GAME_TYPE):
        props[getVarName(field, sess.name)] = getattr(sess, field)

    await getRedis().mset(props)
    logger.debug(f"New session {uid} {props}")
    return sess


async def addPlayer(player: newPlayer) -> Session:
    "Add a player to an existing session"
    sess = await getSession(player.sessionName)

    for p in sess.players:
        if p["name"] == player.name:
            logger.debug(f"Attempt to create same player twice {player.name}")
            raise HTTPException(
                httpstatus.HTTP_409_CONFLICT,
                f"A player called {player.name} already exists",
            )

    pidP = getUniquePlayerId()
    player_info = player.dict()
    del player_info["sessionName"]
    pid = await pidP
    secretId = int((time.time() * 1000) % 3600) + pid
    player_info["id"] = pid
    player_info["_secret"] = secretId
    initialPlayerData = getPlayerInitialData(sess.gameType)

    redisObj = {}
    for name, value in player_info.items():
        redisObj[getVarName(name, player.sessionName, pid)] = value

    for name, value in initialPlayerData:
        redisObj[getVarName(name, player.sessionName, pid, gameData=True)] = value

    async with getRedis().client() as conn:
        push = conn.rpush(getVarName(PLAYERS_ORDER, player.sessionName), pid)
        mset = conn.mset(redisObj)

        pub = publishEvent(
            player.sessionName,
            None,
            cat="newPlayer",
            name=player.name,
            avatar=player.avatar,
            id=pid,
        )
        await push
        await mset
        await pub

    del player_info["_secret"]
    getattr(sess, SESSION_PLAYERS_DATA)[str(pid)] = initialPlayerData
    getattr(sess, SESSION_PLAYERS).append(player_info)
    sess.secret = secretId
    logger.debug(f"New player {pid}")
    return sess


async def restartGame(player: PlayerIdentifier, tasks: BackgroundTasks) -> None:
    """resets a game state"""
    uid = player.sessionName
    async with getRedis().client() as conn:
        gameType = await conn.get(getVarName(SESSION_GAME_TYPE, uid))
        allPlayers = await conn.lrange(getVarName(PLAYERS_ORDER, uid), 0, -1)

        iface = games[gameType]
        newVals = {}
        for name, val in iface.getGameData().items():
            newVals[getVarName(name, uid, gameData=True)] = val
        for name, val in iface.getPlayerData().items():
            for playername in allPlayers:
                newVals[getVarName(name, uid, playername, gameData=True)] = val

        await conn.mset(newVals)
        await publishEvent(uid, conn, cat="restart")

    async def delayedStart():
        await asyncio.sleep(3)
        await _triggerGameStart(iface, uid, getRedis().client())

    tasks.add_task(delayedStart)


async def startGame(player: PlayerIdentifier, tasks: BackgroundTasks) -> None:
    """Notifies that some player is ready to start the game"""
    redis = getRedis()
    async with redis.client() as conn:
        pr = getVarName(PLAYERS_READY, player.sessionName, gameData=True)
        if await conn.sismember(pr, player.id):
            raise HTTPException(httpstatus.HTTP_409_CONFLICT, "Action already done")
        await publishEvent(player.sessionName, conn, cat="ready", player=player.id)
        await conn.sadd(pr, player.id)
        await conn.set(f"S{player.sessionName}:" + SESSION_S_TIME, int(time.time()))

        po = getVarName(PLAYERS_ORDER, player.sessionName)
        nbPlayers = int(await conn.llen(po))

        if nbPlayers <= await conn.scard(pr):

            async def checkStartOfGame():
                await asyncio.sleep(1)
                async with redis.client() as conn:
                    game = games[
                        await conn.get(
                            getVarName(SESSION_GAME_TYPE, player.sessionName)
                        )
                    ]
                    nbPlayersReady = int(await conn.scard(pr))
                    if nbPlayersReady == nbPlayers and (
                        game.max_players or 99
                    ) >= nbPlayersReady >= (game.min_players or 1):
                        # all players are ready!
                        await _triggerGameStart(game, player.sessionName, conn)

            tasks.add_task(checkStartOfGame)


def init(app, config):
    setRedis(aioredis.from_url("redis://" + config.redis_server, decode_responses=True))

    app.post("/c/session/new", response_model=Session)(makeSession)

    app.post(
        "/c/session/join",
        responses={
            409: {"description": "player already joined"},
        },
        response_model=Session,
    )(addPlayer)

    app.post(
        "/c/session/start",
        response_model=None,
        responses={
            409: {"description": "player already started"},
        },
    )(startGame)

    app.post("/c/session/restart", response_model=None)(restartGame)

    app.post("/c/session/vote")(vote)
