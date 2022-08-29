from enum import Enum
from logging import getLogger
from typing import Any, Dict

import aioredis
from pydantic import BaseModel

from ..globalHandlers import (
    getConfig,
    publishEvent,
    getVarName,
    PLAYERS_ORDER,
)
from ..models import SESSION_PLAYERS_DATA, Player, PlayerIdentifier, Session
from .interfaces import Events, GameInterface, stdVar
from .std_implem import def_playerAdded

placements = ["0-0", "6-6", "0-6", "6-0"]


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
    await publishEvent(
        params.player.sessionName,
        cat=Events.varUpdate.name,
        var=gameVars.pawns.name,
        val={params.player.id: [params.position.shortText]},
        player=params.player.id,
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
