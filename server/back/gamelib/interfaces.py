from typing import Dict, Callable, Optional, Any

class GameInterface:
    name : str = "Unknown game"
    description : str = "No description yet"
    long_description : str = "No long description yet"
    card : str = "quiz"
    min_players : Optional[int] = 1
    max_players : Optional[int] = 99

    @staticmethod
    def getPlayerData() -> dict:
        """ Returns initial data for a player """
        return {}

    @staticmethod
    def getGameData() -> dict:
        """ Returns initial data for a game """
        return {}

    actions: Dict[str, Any]  = {}

    # the following should not be overloaded:

    @classmethod
    def info(kls) -> dict[str, str]:
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
    def getPlayerIdentifiers() -> list[str]:
        return ['id', 'name', 'avatar']

    @classmethod
    def definition(kls) -> dict[str, Any]:
        return {kls.name: kls}

    # notification handlers

    @staticmethod
    async def votePassed(sessionId: str, name: str, conn):
        return

    @staticmethod
    async def startGame(sessionId, conn):
        return
