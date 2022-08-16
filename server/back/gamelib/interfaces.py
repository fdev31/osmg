from __future__ import annotations

from typing import Dict, Optional, Any, List, Set
from functools import lru_cache
from aioredis import Redis

from ..models import Session


class GameInterface:
    _info: Dict[str, Any]

    name: str = "Unknown game"
    description: str = "No description yet"
    long_description: str = "No long description yet"
    card: str = "quiz"
    min_players: Optional[int] = 1
    max_players: Optional[int] = 99

    _pds: Set[str]  # player data set cache
    _gds: Set[str]  # game data set cache
    _pdl: Set[str]  # player data list cache
    _gdl: Set[str]  # game data list cache

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
        if getattr(kls, "_pds", None) is None:
            kls._pds = set(
                k for k, v in kls.getPlayerData(sess).items() if isinstance(v, set)
            )
        return kls._pds

    @classmethod
    def getPlayerDataLists(kls, sess: Session) -> set[str]:
        """Returns the lists' name in the player data"""
        if getattr(kls, "_pdl", None) is None:
            kls._pdl = set(
                k for k, v in kls.getPlayerData(sess).items() if isinstance(v, list)
            )
        return kls._pdl

    @classmethod
    def getGameDataSets(kls) -> set[str]:
        """Returns the sets' name in the game data"""
        if getattr(kls, "_gds", None) is None:
            kls._gds = set(
                k for k, v in kls.getGameData().items() if isinstance(v, set)
            )
        return kls._gds

    @classmethod
    def getGameDataLists(kls) -> set[str]:
        """Returns the lists' name in the game data"""
        if getattr(kls, "_gdl", None) is None:
            kls._gdl = set(
                k for k, v in kls.getGameData().items() if isinstance(v, list)
            )
        return kls._gdl

    @classmethod
    def definition(kls) -> Dict[str, Any]:
        return {kls.name: kls}

    @classmethod
    async def playerAdded(kls, sess: Session) -> None:
        pass

    # notification handlers

    @staticmethod
    async def votePassed(sessionId: str, name: str, conn: Redis) -> None:
        return

    @staticmethod
    async def startGame(sessionId: str, conn: Redis) -> None:
        return
