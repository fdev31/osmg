from .interfaces import GameInterface
from typing import Dict, Any


class Game(GameInterface):
    name = "Dummy game"
    card = "quiz"
    description = "A multi-player marathon-like dice game"
    long_description = "blah blah blah"
    min_players = 2
    max_players = None


definition = Game.definition()
