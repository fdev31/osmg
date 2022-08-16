from .interfaces import GameInterface
from logging import getLogger


class Game(GameInterface):
    name = "DummyGame"
    card = "quiz"
    min_players = 2
    max_players = None


logger = getLogger(Game.name)
definition = Game.definition()
