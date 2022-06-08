import random
import logging
from typing import List, Awaitable, Optional

import aioredis
from fastapi import HTTPException
from starlette import status as httpstatus

from ..globalHandlers import (
    getRedis,
    getConfig,
    getGameDataPrefix,
    getVarName,
    publishEvent,
    PLAYERS_ORDER,
)
from ..sessionmanager.public import isPlayerValid
from ..models import PlayerIdentifier
from ..utils import loads, dumps

from .interfaces import GameInterface

ACTIVE_PLAYERS = "curOrder"

logger = logging.getLogger("marathon")


async def isPlayerTurn(
    conn: aioredis.Redis,
    prefix: str,
    playerId: int,
    secret: Optional[int],
) -> bool:
    if not await isPlayerValid(conn, prefix.split(":")[0][1:], playerId, secret):
        return False
    curPlayer = await conn.get(prefix + "curPlayer")
    curPlayerId = await conn.lindex(prefix[:-2] + ACTIVE_PLAYERS, int(curPlayer))
    return int(curPlayerId) == int(playerId)


async def throwDice(player: PlayerIdentifier) -> List[int]:
    """Throw a number of dices (defined by the current player score)"""
    redis = aioredis.from_url("redis://" + getConfig().redis_server, decode_responses=True)
    gprefix = getGameDataPrefix(player.sessionName)
    prefix = getGameDataPrefix(player.sessionName, player.id)
    propName = prefix + "_diceValue"

    async with redis.client() as conn:
        if not await isPlayerTurn(conn, gprefix, player.id, player.secret):
            raise HTTPException(httpstatus.HTTP_403_FORBIDDEN, "Not your turn!")
        tmpDice = await conn.get(propName)
        if tmpDice:
            raise HTTPException(
                httpstatus.HTTP_421_MISDIRECTED_REQUEST, "Dice already thrown"
            )
        remainingDistance = await conn.get(prefix + "distance")

        dices = [
            random.randint(1, 6)
            for x in range(min(4, len(str(int(remainingDistance) - 1))))
        ]
        await conn.set(propName, dumps(dices))
    return dices


async def validateDice(player: PlayerIdentifier, value: str) -> None:
    """Validate a previously thrown dice with a new order
    set value=0 to skip the turn
    """
    redis = getRedis()
    prefix = getGameDataPrefix(player.sessionName, player.id)
    g_prefix = getGameDataPrefix(player.sessionName)
    propName = prefix + "_diceValue"
    newVal = None
    async with redis.client() as conn:
        if not await isPlayerTurn(conn, g_prefix, player.id, player.secret):
            raise HTTPException(httpstatus.HTTP_403_FORBIDDEN, "Not your turn!")
        if value != "0":
            previous = loads(await conn.get(propName))
            current = [int(x) for x in value]
            try:
                for c in current:
                    previous.remove(c)
            except ValueError:
                raise HTTPException(
                    httpstatus.HTTP_421_MISDIRECTED_REQUEST, "Dice not matching"
                )
        await conn.delete(propName)
        propName = prefix + "distance"
        newVal = await conn.decrby(propName, int(value))
        logger.debug(f"{player} decr remaining distance by {value}, it's now {newVal}")
        await publishEvent(
            player.sessionName,
            conn,
            cat="varUpdate",
            var="distance",
            val=newVal,
            player=player.id,
        )
        await turnLogic(newVal, player, conn)


async def declareWinner(session: str, pid: str, conn: aioredis.Redis):
    await publishEvent(
        session, conn, cat="endOfGame", message="We have a winner!", player=pid
    )


async def turnLogic(
    distance: Optional[int], player: PlayerIdentifier, conn: aioredis.Redis = None
):
    if not conn:
        conn = getRedis()

    g_prefix = getGameDataPrefix(player.sessionName)
    po = getVarName(ACTIVE_PLAYERS, player.sessionName)
    nbPlayers = int(await conn.llen(po))
    playerLost = False

    if distance is not None:  # check END OF GAME
        if distance == 0:  # End of game
            await declareWinner(player.sessionName, str(player.id), conn)
            return
        if distance < 0:  # disqualified
            playerLost = True
            nbPlayers -= 1
            await conn.lrem(po, 1, player.id)

        if nbPlayers == 1:  # only one runner left !
            curPlayerId = await conn.lindex(po, 0)
            await declareWinner(player.sessionName, curPlayerId, conn)
            return

        if playerLost:  # we lost a player: no need to increment curPlayer counter
            curPlayer = int(await conn.get(g_prefix + "curPlayer"))
        else:
            curPlayer = int(await conn.incr(g_prefix + "curPlayer"))
    else:  # no distance == check at game startup
        curPlayer = 0

    if curPlayer != None and curPlayer >= nbPlayers:  # end of turn
        turn = await conn.incr(g_prefix + "turns")
        await publishEvent(player.sessionName, conn, cat="newTurn", val=turn)
        await conn.set(g_prefix + "curPlayer", 0)
        curPlayer = 0

    # resolve current player id & publish it
    curPlayerId = await conn.lindex(po, curPlayer)
    await publishEvent(player.sessionName, conn, cat="curPlayer", val=curPlayerId)


class DiceInterface(GameInterface):
    name = "marathon"
    card = "marathon"
    description = "A multi-player marathon-like dice game"
    long_description = "blah blah blah"
    min_players = 2
    max_players = None

    @staticmethod
    async def votePassed(sessionId: str, name: str, conn: aioredis.Redis):
        topic, data = name.split("_", 1)
        if topic == "kick":
            whom = data
            ap = getVarName(ACTIVE_PLAYERS, sessionId)
            cp = getVarName("curPlayer", sessionId, gameData=True)
            cu = int(await conn.get(cp))
            pindex = await conn.lpos(ap, whom)
            if pindex is not None and pindex < cu:
                await conn.decr(cp)
                await conn.lrem(ap, 1, whom)

    @staticmethod
    async def startGame(sessionId: str, conn: aioredis.Redis):
        dump = await conn.lrange(getVarName(PLAYERS_ORDER, sessionId), 0, -1)
        cp = getVarName(ACTIVE_PLAYERS, sessionId)
        await conn.unlink(cp)
        await conn.rpush(cp, *dump)
        await turnLogic(None, PlayerIdentifier(id=0, sessionName=sessionId), conn)

    @staticmethod
    def getPlayerData():
        return dict(distance=42195)

    @staticmethod
    def getGameData():
        return {
            "turns": 0,
            "curPlayer": 0,
        }

    actions = {
        "throwDice": dict(
            handler=throwDice,
            response_model=List[int],
            responses={
                403: {"description": "not your turn"},
                421: {"description": "you already did this action"},
                200: {
                    "description": "returns dices value",
                    "content": {"application/json": {"example": "[4, 6, 2, 1]"}},
                },
            },
        ),
        "validateDice": dict(
            handler=validateDice,
            response_model=None,
            responses={
                403: {
                    "description": "you tried to played but it's another player's turn"
                },
                421: {"description": "cheating attempt detected (wrong dice!)"},
            },
        ),
    }


logger = logging.getLogger(DiceInterface.name)

definition = DiceInterface.definition()
