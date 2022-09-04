from enum import Enum
from typing import Any, Dict, Generator, Optional

from pydantic import BaseModel

from ..models import PlayerIdentifier


class playerConnection(BaseModel):
    isPlayerTurn: bool
    playerIndex: int


class gameVars(str, Enum):
    pawns = "pawns"
    gameOver = "gameOver"


class SimpleReturn(BaseModel):
    "returned when no data is needed"
    ok: bool = True


class Coords(BaseModel):
    """Corrdinates of a pawn on the board.
    starts with zero (0)"""

    x: int
    y: int

    @property
    def shortText(self) -> str:
        return "%d-%d" % (self.x, self.y)


class AtakksAddBody(BaseModel):
    "Parameters for an add call in atakks"
    player: PlayerIdentifier
    reference: Coords
    position: Coords


class AtakksMoveBody(BaseModel):
    "Parameters for a move call in atakks"
    player: PlayerIdentifier
    source: Coords
    destination: Coords
