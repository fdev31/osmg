from enum import Enum
from logging import getLogger
from typing import Any, Dict, Generator, Optional

import aioredis
from fastapi import HTTPException
from pydantic import BaseModel
from starlette import status as httpstatus

MAX_BOARD_INDEX = 6

from pydantic import BaseModel

from ..globalHandlers import (
    getConfig,
    getGameDataPrefix,
    getNewRedis,
    getVarName,
    publishEvent,
)
from ..models import SESSION_PLAYERS_DATA, Player, PlayerIdentifier, Session
from ..sessionmanager.public import isPlayerValid
from .interfaces import Events, GameInterface, sessVar, stdVar
from .std_implem import def_playerAdded

placements = [
    "0-0",
    "%d-%d" % (MAX_BOARD_INDEX, MAX_BOARD_INDEX),
    "0-%d" % MAX_BOARD_INDEX,
    "%d-0" % MAX_BOARD_INDEX,
]

ACTIVE_PLAYERS = "curOrder"


class playerConnection(BaseModel):
    isPlayerTurn: bool
    playerIndex: int


async def getPlayerInfo(
    conn: aioredis.Redis,
    prefix: str,
    playerId: str,
    secret: Optional[int],
) -> playerConnection:
    if not await isPlayerValid(conn, prefix.split(":")[0][1:], playerId, secret):
        return playerConnection(isPlayerTurn=False, playerIndex=-1)
    curPlayer = await conn.get(prefix + Events.curPlayer.name)
    curPlayerId = await conn.lindex(
        prefix[:-2] + sessVar.playerOrder.name, int(curPlayer)
    )
    return playerConnection(
        isPlayerTurn=int(curPlayerId) == int(playerId),
        playerIndex=curPlayer,
    )


class gameVars(str, Enum):
    pawns = "pawns"


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


def generateZoneCoords(x: int, y: int) -> Generator[str, None, None]:
    for lx in range(x - 1, x + 2):
        if lx < 0 or lx > MAX_BOARD_INDEX:
            continue
        for ly in range(y - 1, y + 2):
            if ly < 0 or ly > MAX_BOARD_INDEX:
                continue
            yield f"{lx}-{ly}"


class Summary(BaseModel):
    pawnCount: int = 0
    bestPlayer: str = ""
    bestScore: int = 0


async def _movePawn(
    player: PlayerIdentifier, source: Coords, destination: Coords, move: bool = False
) -> SimpleReturn:
    redis: aioredis.Redis = getNewRedis()
    gprefix: str = getGameDataPrefix(player.sessionName)
    prefix: str = gprefix[:-2]

    async with redis.client() as conn:
        pi = await getPlayerInfo(conn, gprefix, player.id, player.secret)
        if not pi.isPlayerTurn:
            raise HTTPException(httpstatus.HTTP_403_FORBIDDEN, "Not your turn!")

        all_players = await conn.lrange(prefix + sessVar.playerOrder.name, 0, -1)
        my_new_pawns = set([destination.shortText])
        summary = Summary()
        convertible_zone = set(generateZoneCoords(destination.x, destination.y))
        hiScores = {}
        for plr in all_players:
            ppawnVar = getVarName(
                gameVars.pawns.name, player.sessionName, plr, gameData=True
            )
            ppawns = await conn.smembers(ppawnVar)
            nbPawns = len(ppawns)
            if not move and plr == player.id:
                nbPawns += 1
            hiScores[plr] = nbPawns
            summary.pawnCount += nbPawns

            if plr != player.id:
                stolen = ppawns.intersection(convertible_zone)
                if stolen:
                    await conn.srem(ppawnVar, *stolen)
                    my_new_pawns.update(stolen)

        hiScores[player.id] += len(stolen)

        for plr, score in hiScores.items():
            if score > summary.bestScore:
                summary.bestScore = nbPawns
                summary.bestPlayer = plr

        myPawnVar = getVarName(
            gameVars.pawns.name,
            player.sessionName,
            player.id,
            gameData=True,
        )
        if move:
            await conn.srem(ppawnVar, source.shortText)
        await conn.sadd(myPawnVar, *my_new_pawns)

        # move to the next player
        if pi.playerIndex + 1 >= len(all_players):
            await conn.set(gprefix + Events.curPlayer.name, 0)
            curPlayer = 0
        else:
            curPlayer = await conn.incr(gprefix + Events.curPlayer.name)
        curPlayerId = await conn.lindex(
            prefix + sessVar.playerOrder.name, int(curPlayer)
        )

        payload = {player.id: list(my_new_pawns)}

        if move:
            payload["void"] = [source.shortText]

        await publishEvent(
            player.sessionName,
            conn,
            cat=Events.varUpdate.name,
            var=gameVars.pawns.name,
            val=payload,
        )

        if summary.pawnCount == (MAX_BOARD_INDEX + 1) ** 2:
            await publishEvent(
                player.sessionName, conn, cat=Events.endOfGame.name, player=curPlayerId
            )
        else:
            await publishEvent(
                player.sessionName, conn, cat=Events.curPlayer.name, val=curPlayerId
            )
    return SimpleReturn()


async def movePawn(params: AtakksMoveBody) -> SimpleReturn:
    """`player` moves a pawn from `source` to `destination`"""
    logger.debug(f"movePawn({params})")
    return await _movePawn(params.player, params.source, params.destination, True)


async def addPawn(params: AtakksAddBody) -> SimpleReturn:
    """`player` adds a pawn into `positition`, next to `reference`"""
    logger.debug(f"addPawn({params})")
    return await _movePawn(params.player, params.reference, params.position, False)


class Game(GameInterface):
    name = "atakks"
    card = "quiz"
    min_players = 2
    max_players = 4

    @staticmethod
    def getPlayerData(sess: Session) -> Dict[str, Any]:
        pval = placements[len(sess.players)]
        return {
            gameVars.pawns.name: {pval},
        }

    @staticmethod
    def getGameData() -> Dict[str, Any]:
        return {
            stdVar.turns.name: 0,
            stdVar.curPlayer.name: 0,
        }

    @classmethod
    async def playerAdded(kls, sess: Session, player: Player) -> None:
        await def_playerAdded(sess, player)

    @staticmethod
    async def startGame(sessionId: str, conn: aioredis.Redis) -> None:
        curPlayer = await conn.lindex(
            getVarName(sessVar.playerOrder.name, sessionId), 0
        )
        await publishEvent(sessionId, conn, cat=Events.curPlayer.name, val=curPlayer)

    actions: Dict[str, Any] = {
        "add": dict(
            handler=addPawn,
            response_model=SimpleReturn,
            responses={
                403: {"description": "not your turn"},
                421: {"description": "invalid move"},
                200: {
                    "description": "makes a move in atakks",
                    "content": {"application/json": {"ok": True}},
                },
            },
        ),
        "move": dict(
            handler=movePawn,
            response_model=SimpleReturn,
            responses={
                403: {"description": "not your turn"},
                421: {"description": "invalid move"},
                200: {
                    "description": "makes a move in atakks",
                    "content": {"application/json": {"ok": True}},
                },
            },
        ),
    }


logger = getLogger(Game.name)
definition = Game.definition()
