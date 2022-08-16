from logging import getLogger

from .std_implem import def_playerAdded

from .interfaces import GameInterface, Events
from ..models import Session, Player, SESSION_PLAYERS_DATA
from ..globalHandlers import publishEvent
from typing import Dict, Any

placements = ["0-0", "6-6", "0-6", "6-0"]


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

    actions: Dict[str, Any] = {}


logger = getLogger(Game.name)
definition = Game.definition()
