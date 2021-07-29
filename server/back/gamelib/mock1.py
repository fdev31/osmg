from .interfaces import GameInterface


class Game(GameInterface):
    name = "Dummy game"
    card = "quiz"
    description = "A multi-player marathon-like dice game"
    long_description = "blah blah blah"
    min_players = 2
    max_players = None

    @staticmethod
    def getPlayerData():
        return {}

    @staticmethod
    def getGameData():
        return {}

    actions = {}


definition = Game.definition()
