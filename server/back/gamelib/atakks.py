from logging import getLogger
from typing import Any, Dict, Generator, Optional

import aioredis
from fastapi import HTTPException
from pydantic import BaseModel
from starlette import status as httpstatus

from ..globalHandlers import (
    getGameDataPrefix,
    getPlayerGameVar,
    getRedis,
    getSessionVar,
    publishEvent,
)
from ..models import Player, PlayerIdentifier, Session
from ..sessionmanager.public import isPlayerValid
from .atakks_models import (
    AtakksAddBody,
    AtakksMoveBody,
    Coords,
    SimpleReturn,
    gameVars,
    playerConnection,
)
from .interfaces import Events, GameInterface, sessVar, stdVar
from .std_implem import def_playerAdded

MAX_BOARD_INDEX = 6

placements = [
    "0-0",
    "%d-%d" % (MAX_BOARD_INDEX, MAX_BOARD_INDEX),
    "0-%d" % MAX_BOARD_INDEX,
    "%d-0" % MAX_BOARD_INDEX,
]


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


async def buildSummary(
    conn: aioredis.Redis,
    destination: Optional[Coords],
    player: PlayerIdentifier,
    players: list[str],
    selfIncrement: bool = False,
) -> tuple[Summary, set[str]]:
    summary = Summary()
    my_new_pawns = set([destination.shortText]) if destination else set()
    convertible_zone = (
        set(generateZoneCoords(destination.x, destination.y)) if destination else set()
    )
    hiScores = {}
    for plr in players:
        ppawnVar = getPlayerGameVar(gameVars.pawns.name, player.sessionName, plr)
        ppawns = await conn.smembers(ppawnVar)
        nbPawns = len(ppawns)
        if selfIncrement and plr == player.id:
            nbPawns += 1
        hiScores[plr] = nbPawns
        summary.pawnCount += nbPawns

        if plr != player.id:
            stolen = ppawns.intersection(convertible_zone)
            if stolen:
                if destination is not None:
                    await conn.srem(ppawnVar, *stolen)
                my_new_pawns.update(stolen)

    hiScores[player.id] += len(stolen)

    for plr, score in hiScores.items():
        if score > summary.bestScore:
            summary.bestScore = nbPawns
            summary.bestPlayer = plr

    return summary, my_new_pawns


async def _movePawn(
    player: PlayerIdentifier, source: Coords, destination: Coords, move: bool = False
) -> SimpleReturn:
    redis: aioredis.Redis = getRedis()
    gprefix: str = getGameDataPrefix(player.sessionName)
    prefix: str = gprefix[:-2]

    ppawnVar = getPlayerGameVar(gameVars.pawns.name, player.sessionName, player.id)

    async with redis.client() as conn:
        pi = await getPlayerInfo(conn, gprefix, player.id, player.secret)
        if not pi.isPlayerTurn:
            raise HTTPException(httpstatus.HTTP_403_FORBIDDEN, "Not your turn!")

        all_players = await conn.lrange(prefix + sessVar.playerOrder.name, 0, -1)
        summary, pawnsConverted = await buildSummary(
            conn, destination, player, all_players, selfIncrement=not move
        )

        myPawnVar = getPlayerGameVar(
            gameVars.pawns.name,
            player.sessionName,
            player.id,
        )
        if move:
            await conn.srem(ppawnVar, source.shortText)
        await conn.sadd(myPawnVar, *pawnsConverted)

        # move to the next player
        if pi.playerIndex + 1 >= len(all_players):
            await conn.set(gprefix + Events.curPlayer.name, 0)
            curPlayer = 0
        else:
            curPlayer = await conn.incr(gprefix + Events.curPlayer.name)
        curPlayerId = await conn.lindex(
            prefix + sessVar.playerOrder.name, int(curPlayer)
        )

        payload = {player.id: list(pawnsConverted)}

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
                player.sessionName,
                conn,
                cat=Events.endOfGame.name,
                player=summary.bestPlayer,
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


async def surrender(player: PlayerIdentifier) -> SimpleReturn:
    # if someone surrenders, just compute the best scores & claim end of game
    logger.debug(f"surrender({player})")
    async with getRedis().client() as conn:
        all_players = await conn.lrange(
            getSessionVar(sessVar.playerOrder.name, player.sessionName), 0, -1
        )
        summary, _pawnsConverted = await buildSummary(
            conn, None, player, all_players, selfIncrement=False
        )
        await publishEvent(
            player.sessionName,
            conn,
            cat=Events.endOfGame.name,
            player=summary.bestPlayer,
        )
    return SimpleReturn()


class Game(GameInterface):
    name = "atakks"
    card = "atakks"
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
            getSessionVar(sessVar.playerOrder.name, sessionId), 0
        )
        await publishEvent(sessionId, conn, cat=Events.curPlayer.name, val=curPlayer)

    actions: Dict[str, Any] = {
        "surrender": dict(
            handler=surrender,
            response_model=SimpleReturn,
            responses={
                200: {
                    "description": "makes a move in atakks",
                    "content": {"application/json": {"ok": True}},
                },
            },
        ),
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
