from pydantic import BaseModel
from typing import List, Dict, Optional

__all__ = ["Player", "newPlayer", "Session"]


class PlayerIdentifier(BaseModel):
    "identifies a user"
    id: int
    sessionName: str
    secret: Optional[int] = None


class _BasePlayer(BaseModel):
    name: str
    avatar: str


class Player(_BasePlayer, PlayerIdentifier):
    "Participant to a game session"


class newPlayer(_BasePlayer):
    "Player with associated session to join"
    sessionName: str


class RedisSession(BaseModel):
    "Game instance description & states as stored in Redis"
    gameType: str
    creationTime: int
    startTime: int = 0


class Session(RedisSession):
    "Game instance description & states"
    gameData: dict = {}
    playersData: Dict = {}
    players: List[dict] = []
    name: str
    secret: Optional[int] = None


_propCache = {}


def getPropertieList(kls):
    if kls not in _propCache:
        _propCache[kls] = list(kls.schema()["properties"].keys())
    return _propCache[kls]


SESSION_GAME_TYPE = "gameType"
SESSION_NAME = "name"
SESSION_C_TIME = "creationTime"
SESSION_S_TIME = "startTime"
SESSION_PLAYERS = "players"
SESSION_PLAYERS_DATA = "playersData"
SESSION_GAME_DATA = "gameData"
