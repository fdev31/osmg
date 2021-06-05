from pydantic import BaseModel
from typing import List

__all__ = ['Player', 'newPlayer', 'Session']

class Player(BaseModel):
    " Participant to a game session "
    name: str
    avatar: str
    id: int

class newPlayer(Player):
    " Player with associated session to join "
    sessionName: str

class Session(BaseModel):
    " Game instance description & states "
    players: List[Player] = []
    name: str
    gameType: str = "dice"
    gameData: dict = {}
    creationTime: int

