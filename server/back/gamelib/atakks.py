from enum import Enum
from logging import getLogger
from typing import Any, Dict, Optional

from fastapi import HTTPException
from starlette import status as httpstatus
import aioredis
from pydantic import BaseModel
from ..sessionmanager.public import isPlayerValid

from ..globalHandlers import (
    getConfig,
    publishEvent,
    getGameDataPrefix,
    getVarName,
    PLAYERS_ORDER,
)
from ..models import SESSION_PLAYERS_DATA, Player, PlayerIdentifier, Session
from .interfaces import Events, GameInterface, stdVar
from .std_implem import def_playerAdded

placements = ["0-0", "6-6", "0-6", "6-0"]

ACTIVE_PLAYERS = "curOrder"


async def isPlayerTurn(
    conn: aioredis.Redis,
    prefix: str,
    playerId: int,
    secret: Optional[int],
) -> bool:
    if not await isPlayerValid(conn, prefix.split(":")[0][1:], playerId, secret):
        return False
    curPlayer = await conn.get(prefix + Events.curPlayer.name)
    curPlayerId = await conn.lindex(prefix[:-2] + PLAYERS_ORDER, int(curPlayer))
    return int(curPlayerId) == int(playerId)


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


async def addPawn(params: AtakksAddBody) -> SimpleReturn:
    """`player` adds a pawn into `positition`, next to `reference`"""
    redis = aioredis.from_url(
        "redis://" + getConfig().redis_server, decode_responses=True
    )
    gprefix = getGameDataPrefix(params.player.sessionName)
    # prefix = getGameDataPrefix(params.player.sessionName, params.player.id)

    async with redis.client() as conn:
        if not await isPlayerTurn(
            conn, gprefix, params.player.id, params.player.secret
        ):
            raise HTTPException(httpstatus.HTTP_403_FORBIDDEN, "Not your turn!")
        # TODO: store value

        curPlayer = int(await conn.incr(gprefix + Events.curPlayer.name))
        curPlayerId = await conn.lindex(gprefix[:-2] + PLAYERS_ORDER, int(curPlayer))
        if curPlayerId is None:
            # await publishEvent(params.player.sessionName, conn, cat=Events.newTurn.name, val=turn)
            curPlayer = 0
            await conn.set(gprefix + Events.curPlayer.name, curPlayer)
            curPlayerId = await conn.lindex(
                gprefix[:-2] + PLAYERS_ORDER, int(curPlayer)
            )
        await publishEvent(
            params.player.sessionName,
            conn,
            cat=Events.varUpdate.name,
            var=gameVars.pawns.name,
            val={params.player.id: [params.position.shortText]},
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
        curPlayer = await conn.lindex(getVarName(PLAYERS_ORDER, sessionId), 0)
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
