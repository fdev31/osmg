from .interfaces import GameInterface
from typing import Dict, Any


class Game(GameInterface):
    name = "Super dummy game v2"
    card = "arcade"
    description = "A multi-player marathon-like dice game"
    long_description = "blah blah blah"
    min_players = 2
    max_players = 10

    @staticmethod
    def getPlayerData():
        return {}

    @staticmethod
    def getGameData():
        return {}

    actions: Dict[str, Any] = {}


definition = Game.definition()
