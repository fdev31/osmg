from typing import Dict, Callable, Optional, Any

class GameInterface:
    name : str = "Unknown game"
    description : str = "No description yet"
    long_description : str = "No long description yet"
    card : str = "quiz"
    min_players : Optional[int] = None
    max_players : Optional[int] = None

    @staticmethod
    async def startGame(sessionId, conn):
        return

    @staticmethod
    def getPlayerData():
        return {}

    @staticmethod
    def getGameData():
        return {}

    actions: Dict[str, Any]  = {}

    # the following should not be overloaded:

    @classmethod
    def info(kls):
        if not hasattr(kls, '_info'):
            return {
                "name": kls.name,
                "description": kls.description,
                "long_description": kls.long_description,
                "max_p": kls.max_players,
                "min_p": kls.min_players,
                "card": kls.card,
            }
        return kls._info

    @staticmethod
    def getPlayerIdentifiers():
        return ['id', 'name', 'avatar']

    @classmethod
    def definition(kls):
        return {kls.name: kls}
