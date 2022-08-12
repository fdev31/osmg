from .interfaces import GameInterface
from typing import Dict, Any, List


class Pawn:
    x: int
    y: int


class Game(GameInterface):
    name = "atakks"
    card = "arcade"
    description = "A simpler Go game alternative"
    long_description = "Play against your friends in this simple yet addictive game!"
    min_players = 2
    max_players = 4

    @staticmethod
    def getPlayerData():
        return {
            "pawns": [],
        }

    @staticmethod
    def getGameData():
        return {
            "turns": 0,
            "curPlayer": 0,
        }

    actions: Dict[str, Any] = {}


definition = Game.definition()
