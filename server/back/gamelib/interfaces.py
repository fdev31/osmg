from __future__ import annotations

from typing import Dict, Optional, Any, List
from functools import lru_cache

from ..models import Session


class GameInterface:
    _info: Dict[str, Any]

    name: str = "Unknown game"
    description: str = "No description yet"
    long_description: str = "No long description yet"
    card: str = "quiz"
    min_players: Optional[int] = 1
    max_players: Optional[int] = 99

    @staticmethod
    def getPlayerData(sess: Session) -> Dict[str, Any]:
        """Returns initial data for a player"""
        return {}

    @staticmethod
    def getGameData() -> Dict[str, Any]:
        """Returns initial data for a game"""
        return {}

    actions: Dict[str, Any] = {}

    # the following should not be overloaded:

    @classmethod
    def info(kls) -> Dict[str, Any]:
        if not hasattr(kls, "_info") or kls._info is None:
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
    def getPlayerIdentifiers() -> List[str]:
        return ["id", "name", "avatar"]

    @classmethod
    def getPlayerDataSets(kls, sess: Session) -> set[str]:
        """Returns the sets' name in the player data"""
        return set(k for k, v in kls.getPlayerData(sess).items() if isinstance(v, set))

    @classmethod
    def getPlayerDataLists(kls, sess: Session) -> set[str]:
        """Returns the lists' name in the player data"""
        return set(k for k, v in kls.getPlayerData(sess).items() if isinstance(v, list))

    @classmethod
    @lru_cache(1)
    def getGameDataSets(kls) -> set[str]:
        """Returns the sets' name in the game data"""
        return set(k for k, v in kls.getGameData().items() if isinstance(v, set))

    @staticmethod
    @lru_cache(1)
    def getGameDataLists(kls) -> set[str]:
        """Returns the lists' name in the game data"""
        return set(k for k, v in kls.getGameData().items() if isinstance(v, list))

    @classmethod
    def definition(kls) -> Dict[str, Any]:
        return {kls.name: kls}

    # notification handlers

    @staticmethod
    async def votePassed(sessionId: str, name: str, conn):
        return

    @staticmethod
    async def startGame(sessionId, conn):
        return
