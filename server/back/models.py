from pydantic import BaseModel
from typing import List, Dict

__all__ = ['Player', 'newPlayer', 'Session']

class PlayerIdentifier(BaseModel):
    " identifies a user "
    id: int
    sessionName: str

class _BasePlayer(BaseModel):
    name: str
    avatar: str

class Player(_BasePlayer, PlayerIdentifier):
    " Participant to a game session "

class newPlayer(_BasePlayer):
    " Player with associated session to join "
    sessionName: str

class Session(BaseModel):
    " Game instance description & states "
    players: List[dict] = []
    name: str
    gameType: str = "marathon"
    gameData: dict = {}
    playersData: Dict = {}
    creationTime: int
    startTime: int = 0
