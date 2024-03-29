import asyncio
import logging
import time
from typing import Any

import redis.asyncio as redis
from fastapi import BackgroundTasks, FastAPI, HTTPException
from starlette import status as httpstatus

from ..gamelib.interfaces import Events, GameInterface, sessVar
from ..globalHandlers import (
    getGameVar,
    getNewRedis,
    getPlayerGameVar,
    getPlayerVar,
    getRedis,
    getSessionVar,
    publishEvent,
    setConfig,
    setRedis,
)
from ..models import Player, PlayerIdentifier, Session, newPlayer
from ..utils import ODict
from .base import genUniqueSessionId, getUniquePlayerId
from .library import games, getGameInitialData, getPlayerInitialData
from .public import getSession
from .votesystem import vote

logger = logging.getLogger("Session")


async def _triggerGameStart(game: GameInterface, uid: str, conn: redis.Redis) -> None:
    await publishEvent(
        uid,
        conn,
        cat="start",
        msg="game started",
        max=game.max_players,
        min=game.min_players,
    )
    await game.startGame(uid, conn)


async def _resetSession(
    sess: Session, conn: redis.Redis | None = None
) -> tuple[Session, dict[str, Any]]:
    mprops = {}
    props, lists, sets = getGameInitialData(sess.gameType)

    for name, value in props.items():
        mprops[getGameVar(name, sess.name)] = value
        sess.gameData[name] = value

    sess.gameData.update(lists)
    sess.gameData.update(sets)

    for field in (sessVar.c_time.value, sessVar.name.value, sessVar.gameType.value):
        mprops[getSessionVar(field, sess.name)] = getattr(sess, field)

    async with (conn or getRedis()) as conn:
        await conn.mset(mprops)
        for k, v in lists.items():
            if v:
                await conn.rpush(getGameVar(k, sess.name), *v)
        for k, v in sets.items():
            if v:
                await conn.sadd(getGameVar(k, sess.name), *v)

    for k, o in lists.items():
        props[k] = o
    for k, o in sets.items():
        props[k] = list(o)

    logger.debug(f"Cleared session: {sess.name}")
    return sess, props


async def makeSession(gameType: str) -> Session:
    "Create a new emtpy session with no players"
    uid = await genUniqueSessionId()
    sess = Session(
        name=uid, players=[], creationTime=int(time.time()), gameType=gameType
    )
    logger.debug(f"New session: {sess.name}")
    return (await _resetSession(sess))[0]


async def _clearPlayer(
    sess: Session, pid: str, conn: redis.Redis | None = None
) -> dict[str, Any]:
    (
        initialPlayerData,
        initialPlayerDataLists,
        initialPlayerDataSets,
    ) = getPlayerInitialData(sess)

    redisObj = {}
    for name, value in initialPlayerData.items():
        redisObj[getPlayerGameVar(name, sess.name, pid)] = value

    async with (conn or getRedis().client()) as conn:
        if redisObj:
            mset = conn.mset(redisObj)

        for k, v in initialPlayerDataSets.items():
            if v:
                await conn.sadd(getPlayerGameVar(k, sess.name, playerId=pid), *v)
        for k, v in initialPlayerDataLists.items():
            if v:
                await conn.rpush(getPlayerGameVar(k, sess.name, playerId=pid), *v)
        if redisObj:
            await mset

    initialPlayerData = dict(initialPlayerData)
    # add sets & lists to player data
    for k, v in initialPlayerDataLists.items():
        initialPlayerData[k] = v
    for k, v in initialPlayerDataSets.items():
        initialPlayerData[k] = list(v)
    return initialPlayerData


async def addPlayer(player: newPlayer) -> Session:
    "Add a player to an existing session"
    sess = await getSession(player.sessionName)
    game = games[sess.gameType]

    for p in sess.players:
        if p["name"] == player.name:
            logger.debug(f"Attempt to create same player twice {player.name}")
            raise HTTPException(
                httpstatus.HTTP_409_CONFLICT,
                f"A player called {player.name} already exists",
            )

    # TODO: simplify using _clearPlayer
    pidP = getUniquePlayerId()
    player_info = player.dict()
    del player_info["sessionName"]
    pid = await pidP
    spid = str(pid)
    secretId = int((time.time() * 1000) % 3600) + pid
    player_info["id"] = spid
    player_info["_secret"] = secretId
    (
        initialPlayerData,
        initialPlayerDataLists,
        initialPlayerDataSets,
    ) = getPlayerInitialData(sess)

    redisObj = {}
    for name, value in player_info.items():
        redisObj[getPlayerVar(name, player.sessionName, spid)] = value

    for name, value in initialPlayerData.items():
        redisObj[getPlayerGameVar(name, player.sessionName, spid)] = value

    async with getRedis().client() as conn:
        push = conn.rpush(
            getSessionVar(sessVar.playerOrder.name, player.sessionName), spid
        )
        mset = conn.mset(redisObj)

        for k, v in initialPlayerDataSets.items():
            if v:
                await conn.sadd(
                    getPlayerGameVar(k, player.sessionName, playerId=spid), *v
                )
        for k, v in initialPlayerDataLists.items():
            if v:
                await conn.rpush(
                    getPlayerGameVar(k, player.sessionName, playerId=spid), *v
                )

        await push
        await mset

    del player_info["_secret"]
    initialPlayerData = dict(initialPlayerData)
    # add sets & lists to player data
    for k, v in initialPlayerDataLists.items():
        initialPlayerData[k] = v
    for k, v in initialPlayerDataSets.items():
        initialPlayerData[k] = list(v)
    getattr(sess, sessVar.playersData.name)[spid] = initialPlayerData
    getattr(sess, sessVar.players.name).append(player_info)
    sess.secret = secretId
    fullPlayer = player.dict()
    fullPlayer["id"] = spid
    await game.playerAdded(sess, Player(**fullPlayer))
    logger.debug(f"New player {pid}")
    return sess


async def restartGame(player: PlayerIdentifier, tasks: BackgroundTasks) -> None:
    """resets a game state"""
    uid = player.sessionName
    async with getRedis().client() as conn:
        gameType = await conn.get(getSessionVar(sessVar.gameType.name, uid))
        allPlayers = await conn.lrange(
            getSessionVar(sessVar.playerOrder.name, uid), 0, -1
        )

        iface = games[gameType]
        playersData = {}

        sess, gameData = await _resetSession(
            Session(name=player.sessionName, creationTime=0, gameType=gameType), conn
        )
        for playername in allPlayers:
            playersData[playername] = await _clearPlayer(sess, playername, conn)

        await publishEvent(
            uid,
            conn,
            cat="restart",
            game=gameType,
            playersData=playersData,
            gameData=gameData,
        )

    async def delayedStart() -> None:
        await asyncio.sleep(3)
        await _triggerGameStart(iface, uid, getRedis().client())

    tasks.add_task(delayedStart)


async def startGame(player: PlayerIdentifier, tasks: BackgroundTasks) -> None:
    """Notifies that some player is ready to start the game"""
    redis = getRedis()
    async with redis.client() as conn:
        pr = getSessionVar(sessVar.playersReady.name, player.sessionName)
        if await conn.sismember(pr, player.id):
            raise HTTPException(httpstatus.HTTP_409_CONFLICT, "Action already done")
        await publishEvent(
            player.sessionName, conn, cat=Events.ready.name, id=str(player.id)
        )
        await conn.sadd(pr, player.id)
        await conn.set(
            f"S{player.sessionName}:" + sessVar.s_time.value, int(time.time())
        )

        po = getSessionVar(sessVar.playerOrder.name, player.sessionName)
        nbPlayers = int(await conn.llen(po))

        if nbPlayers <= await conn.scard(pr):

            async def checkStartOfGame() -> None:
                await asyncio.sleep(1)
                async with redis.client() as conn:
                    game = games[
                        await conn.get(
                            getSessionVar(sessVar.gameType.name, player.sessionName)
                        )
                    ]
                    nbPlayersReady = int(await conn.scard(pr))
                    if nbPlayersReady == nbPlayers and (
                        game.max_players or 99
                    ) >= nbPlayersReady >= (game.min_players or 1):
                        # all players are ready!
                        await _triggerGameStart(game, player.sessionName, conn)

            tasks.add_task(checkStartOfGame)


def init(app: FastAPI, config: ODict) -> None:
    setConfig(config)
    setRedis(getNewRedis())

    app.get("/c/session/new", response_model=Session)(makeSession)

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
