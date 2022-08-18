from logging import getLogger
from typing import Any, Dict

import aioredis
from pydantic import BaseModel

from ..globalHandlers import getConfig, getGameDataPrefix, publishEvent
from ..models import SESSION_PLAYERS_DATA, Player, PlayerIdentifier, Session
from .interfaces import Events, GameInterface
from .std_implem import def_playerAdded

placements = ["0-0", "6-6", "0-6", "6-0"]


class Coords(BaseModel):
    """Corrdinates of a pawn on the board.
    starts with zero (0)"""

    x: int
    y: int


class AtakksAddBody(BaseModel):
    "Parameters for an add call in atakks"
    player: PlayerIdentifier
    reference: Coords
    positition: Coords


class AtakksMoveBody(BaseModel):
    "Parameters for a move call in atakks"
    player: PlayerIdentifier
    source: Coords
    destination: Coords


async def addPawn(params: AtakksAddBody) -> bool:
    """`player` adds a pawn into `positition`, next to `reference`"""
    return True


async def movePawn(params: AtakksMoveBody) -> bool:
    """`player` moves a pawn from `source` to `destination`"""
    redis = aioredis.from_url(
        "redis://" + getConfig().redis_server, decode_responses=True
    )
    gprefix = getGameDataPrefix(params.player.sessionName)
    prefix = getGameDataPrefix(params.player.sessionName, player.id)
    return True


class Game(GameInterface):
    name = "atakks"
    card = "arcade"
    min_players = 2
    max_players = 4

    @staticmethod
    def getPlayerData(sess: Session) -> Dict[str, Any]:
        pval = placements[len(sess.players)]
        return {
            "pawns": {pval},
        }

    @staticmethod
    def getGameData() -> Dict[str, Any]:
        return {
            "turns": 0,
            "curPlayer": 0,
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
                    "content": {"application/json": {"success": True}},
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
                    "content": {"application/json": {"success": True}},
                },
            },
        ),
    }


logger = getLogger(Game.name)
definition = Game.definition()
