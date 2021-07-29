from .interfaces import GameInterface


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

    actions = {}


definition = Game.definition()
