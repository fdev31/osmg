from .interfaces import GameInterface
from ..models import Session
from typing import Dict, Any

placements = ["0-0", "6-6", "0-6", "6-0"]


class Game(GameInterface):
    name = "atakks"
    card = "arcade"
    description = "A simpler Go game alternative"
    long_description = "Play against your friends in this simple yet addictive game!"
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

    actions: Dict[str, Any] = {}


definition = Game.definition()
