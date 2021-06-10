from typing import Optional

class GameInterface:
    name : str = "Unknown game"
    description : str = "No description yet"
    long_description : str = "No long description yet"
    card : str = "quiz"
    min_players : Optional[int] = None
    max_players : Optional[int] = None

    @classmethod
    def info(kls):
        return {
            "name": kls.name,
            "description": kls.description,
            "long_description": kls.long_description,
            "max_p": kls.max_players,
            "min_p": kls.min_players,
            "card": kls.card,
        }

    @staticmethod
    def getPlayerData():
        return {}

    @staticmethod
    def getGameData():
        return {}

    actions = {}

    @classmethod
    def definition(kls):
        return {kls.name: kls}
