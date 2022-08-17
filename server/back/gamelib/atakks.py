from logging import getLogger

from .std_implem import def_playerAdded

from .interfaces import GameInterface, Events
from ..models import PlayerIdentifier, Session, Player, SESSION_PLAYERS_DATA
from ..globalHandlers import getConfig, getGameDataPrefix, publishEvent
from typing import Dict, Any
from pydantic import BaseModel
import aioredis

placements = ["0-0", "6-6", "0-6", "6-0"]


class Coords(BaseModel):
    x: int
    y: int


async def addPawn(
    player: PlayerIdentifier, reference: Coords, positition: Coords
) -> bool:
    """`player` adds a pawn into `positition`, next to `reference`"""
    return True


async def movePawn(
    player: PlayerIdentifier, source: Coords, destination: Coords
) -> bool:
    """`player` moves a pawn from `source` to `destination`"""
    redis = aioredis.from_url(
        "redis://" + getConfig().redis_server, decode_responses=True
    )
    gprefix = getGameDataPrefix(player.sessionName)
    prefix = getGameDataPrefix(player.sessionName, player.id)
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
