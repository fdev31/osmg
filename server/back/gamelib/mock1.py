from logging import getLogger

from .interfaces import GameInterface


class Game(GameInterface):
    name = "DummyGame"
    card = "arcade"
    min_players = 2
    max_players = None


logger = getLogger(Game.name)
definition = Game.definition()
