from enum import Enum
from logging import getLogger
from typing import Any, Dict

import aioredis
from pydantic import BaseModel

from ..globalHandlers import getConfig, getGameDataPrefix, publishEvent
from ..models import SESSION_PLAYERS_DATA, Player, PlayerIdentifier, Session
from .interfaces import Events, GameInterface, stdVar
from .std_implem import def_playerAdded

placements = ["0-0", "6-6", "0-6", "6-0"]


class gameVars(str, Enum):
    pawns = "pawns"


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


async def addPawn(params: AtakksAddBody) -> bool:
    """`player` adds a pawn into `positition`, next to `reference`"""
    await publishEvent(
        params.player.sessionName,
        cat=Events.varUpdate.name,
        var=gameVars.pawns.name,
        val={params.player.id: [params.position.shortText]},
        player=params.player.id,
    )
    return True


async def movePawn(params: AtakksMoveBody) -> bool:
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
    return True


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

    actions: Dict[str, Any] = {
        "add": dict(
            handler=addPawn,
            response_model=bool,
            responses={
                403: {"description": "not your turn"},
                421: {"description": "invalid move"},
                200: {
                    "description": "makes a move in atakks",
                    "content": {"application/json": True},
                },
            },
        ),
        "move": dict(
            handler=movePawn,
            response_model=bool,
            responses={
                403: {"description": "not your turn"},
                421: {"description": "invalid move"},
                200: {
                    "description": "makes a move in atakks",
                    "content": {"application/json": True},
                },
            },
        ),
    }


logger = getLogger(Game.name)
definition = Game.definition()
