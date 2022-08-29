from enum import Enum
from logging import getLogger
from typing import Any, Dict, Optional, Generator

import aioredis
from fastapi import HTTPException
from pydantic import BaseModel
from starlette import status as httpstatus

MAX_BOARD_INDEX = 6

from ..globalHandlers import (
    getConfig,
    getGameDataPrefix,
    getVarName,
    publishEvent,
)
from ..models import SESSION_PLAYERS_DATA, Player, PlayerIdentifier, Session
from ..sessionmanager.public import isPlayerValid
from .interfaces import Events, GameInterface, stdVar, sessVar
from .std_implem import def_playerAdded
from pydantic import BaseModel

placements = [
    "0-0",
    "%d-%d" % (MAX_BOARD_INDEX, MAX_BOARD_INDEX),
    "0-%d" % MAX_BOARD_INDEX,
    "%d-0" % MAX_BOARD_INDEX,
]

ACTIVE_PLAYERS = "curOrder"


class playerConnection(BaseModel):
    isPlayerTurn: bool
    playerIndex: int


async def getPlayerInfo(
    conn: aioredis.Redis,
    prefix: str,
    playerId: str,
    secret: Optional[int],
) -> playerConnection:
    if not await isPlayerValid(conn, prefix.split(":")[0][1:], playerId, secret):
        return playerConnection(isPlayerTurn=False, playerIndex=-1)
    curPlayer = await conn.get(prefix + Events.curPlayer.name)
    curPlayerId = await conn.lindex(
        prefix[:-2] + sessVar.playerOrder.name, int(curPlayer)
    )
    return playerConnection(
        isPlayerTurn=int(curPlayerId) == int(playerId),
        playerIndex=curPlayer,
    )


class gameVars(str, Enum):
    pawns = "pawns"


class SimpleReturn(BaseModel):
    "returned when no data is needed"
    ok: bool = True


class Coords(BaseModel):
    """Corrdinates of a pawn on the board.
    starts with zero (0)"""

    x: int
    y: int

    @property
    def shortText(self) -> str:
        return "%d-%d" % (self.x, self.y)


class AtakksAddBody(BaseModel):
    "Parameters for an add call in atakks"
    player: PlayerIdentifier
    reference: Coords
    position: Coords


class AtakksMoveBody(BaseModel):
    "Parameters for a move call in atakks"
    player: PlayerIdentifier
    source: Coords
    destination: Coords


def generateZoneCoords(x: int, y: int) -> Generator[str, None, None]:
    logger.warn(f"generate for {x} & {y}")
    for lx in range(x - 1, x + 2):
        if lx < 0 or lx > MAX_BOARD_INDEX:
            continue
        for ly in range(y - 1, y + 2):
            if ly < 0 or ly > MAX_BOARD_INDEX:
                continue
            yield f"{lx}-{ly}"


async def addPawn(params: AtakksAddBody) -> SimpleReturn:
    """`player` adds a pawn into `positition`, next to `reference`"""
    redis = aioredis.from_url(
        "redis://" + getConfig().redis_server, decode_responses=True
    )
    gprefix = getGameDataPrefix(params.player.sessionName)
    prefix = gprefix[:-2]

    async with redis.client() as conn:
        pi = await getPlayerInfo(conn, gprefix, params.player.id, params.player.secret)
        if not pi.isPlayerTurn:
            raise HTTPException(httpstatus.HTTP_403_FORBIDDEN, "Not your turn!")

        all_players = await conn.lrange(prefix + sessVar.playerOrder.name, 0, -1)
        my_new_pawns = set([params.position.shortText])
        convertible_zone = set(generateZoneCoords(params.position.x, params.position.y))
        for player in all_players:
            ppawnVar = getVarName(
                gameVars.pawns.name, params.player.sessionName, player, gameData=True
            )
            ppawns = await conn.smembers(ppawnVar)
            stolen = ppawns.intersection(convertible_zone)
            if stolen:
                await conn.srem(ppawnVar, *stolen)
                my_new_pawns.update(stolen)

        await conn.sadd(
            getVarName(
                gameVars.pawns.name,
                params.player.sessionName,
                params.player.id,
                gameData=True,
            ),
            *my_new_pawns,
        )

        # move to the next player
        if pi.playerIndex + 1 >= len(all_players):
            await conn.set(gprefix + Events.curPlayer.name, 0)
            curPlayer = 0
        else:
            curPlayer = await conn.incr(gprefix + Events.curPlayer.name)
        curPlayerId = await conn.lindex(
            prefix + sessVar.playerOrder.name, int(curPlayer)
        )
        await publishEvent(
            params.player.sessionName,
            conn,
            cat=Events.varUpdate.name,
            var=gameVars.pawns.name,
            val={params.player.id: list(my_new_pawns)},
        )

        await publishEvent(
            params.player.sessionName, conn, cat=Events.curPlayer.name, val=curPlayerId
        )
    return SimpleReturn()


async def movePawn(params: AtakksMoveBody) -> SimpleReturn:
    """`player` moves a pawn from `source` to `destination`"""
    redis = aioredis.from_url(
        "redis://" + getConfig().redis_server, decode_responses=True
    )
    # gprefix = getGameDataPrefix(params.player.sessionName)
    # prefix = getGameDataPrefix(params.player.sessionName, params.player.id)
    await publishEvent(
        params.player.sessionName,
        redis,
        cat=Events.varUpdate.name,
        var=gameVars.pawns.name,
        val={
            "void": [params.source.shortText],
            params.player.id: [params.destination.shortText],
        },
        player=params.player.id,
    )
    return SimpleReturn()


class Game(GameInterface):
    name = "atakks"
    card = "quiz"
    min_players = 2
    max_players = 4

    @staticmethod
    def getPlayerData(sess: Session) -> Dict[str, Any]:
        pval = placements[len(sess.players)]
        return {
            gameVars.pawns.name: {pval},
        }

    @staticmethod
    def getGameData() -> Dict[str, Any]:
        return {
            stdVar.turns.name: 0,
            stdVar.curPlayer.name: 0,
        }

    @classmethod
    async def playerAdded(kls, sess: Session, player: Player) -> None:
        await def_playerAdded(sess, player)

    @staticmethod
    async def startGame(sessionId: str, conn: aioredis.Redis) -> None:
        curPlayer = await conn.lindex(
            getVarName(sessVar.playerOrder.name, sessionId), 0
        )
        await publishEvent(sessionId, conn, cat=Events.curPlayer.name, val=curPlayer)

    actions: Dict[str, Any] = {
        "add": dict(
            handler=addPawn,
            response_model=SimpleReturn,
            responses={
                403: {"description": "not your turn"},
                421: {"description": "invalid move"},
                200: {
                    "description": "makes a move in atakks",
                    "content": {"application/json": {"ok": True}},
                },
            },
        ),
        "move": dict(
            handler=movePawn,
            response_model=SimpleReturn,
            responses={
                403: {"description": "not your turn"},
                421: {"description": "invalid move"},
                200: {
                    "description": "makes a move in atakks",
                    "content": {"application/json": {"ok": True}},
                },
            },
        ),
    }


logger = getLogger(Game.name)
definition = Game.definition()
