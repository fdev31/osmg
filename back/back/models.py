from pydantic import BaseModel
from typing import List, Dict

__all__ = ['Player', 'newPlayer', 'Session']

class _BasePlayer(BaseModel):
    name: str
    avatar: str

class Player(_BasePlayer):
    " Participant to a game session "
    id: int

class newPlayer(_BasePlayer):
    " Player with associated session to join "
    sessionName: str

class Session(BaseModel):
    " Game instance description & states "
    players: List[Player] = []
    name: str
    gameType: str = "dice"
    gameData: dict = {}
    playersData: Dict = {}
    creationTime: int

