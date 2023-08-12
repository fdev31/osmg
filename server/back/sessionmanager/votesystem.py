import logging
import re
from typing import Any, Callable, Coroutine, Match, Optional, Tuple

import redis
from fastapi import HTTPException
from starlette import status as httpstatus

from ..gamelib.interfaces import sessVar
from ..globalHandlers import getRedis, getVarName, publishEvent
from ..models import PlayerIdentifier
from .public import getGameBySessionId, isPlayerValid

VOTE_IN_PROGRESS = "_voteInProgress"
logger = logging.getLogger("SessionVote")


# Internal handlers definition


async def kickPlayer(conn: redis.Redis, sessionId: str, match: Match[str]) -> None:
    whom = match.groups()[0]
    # remove session info
    await conn.lrem(getVarName(sessVar.playerOrder.name, sessionId), 1, whom)
    await conn.srem(getVarName(sessVar.playersOnline.name, sessionId), whom)
    await conn.srem(getVarName(sessVar.playersReady.name, sessionId), whom)
    # remove vote info
    vip = getVarName(VOTE_IN_PROGRESS, whom)
    await conn.srem(vip, whom)
    # done
    await _checkVoteEnd(conn, sessionId, "kick_" + whom)
    await publishEvent(sessionId, conn, cat="kickPlayer", id=whom)


votesHandlers = {
    re.compile("kick_(.*)"): kickPlayer,
}

# main functions


def findHandler(
    name: str,
) -> Tuple[
    Optional[Match[str]],
    Optional[Callable[[redis.Redis, str, Match[str]], Coroutine[Any, Any, Any]]],
]:
    for handler in votesHandlers:
        m = handler.match(name)
        if m:
            return (m, votesHandlers[handler])
    return (None, None)


async def vote(
    player: PlayerIdentifier, name: str, validate: bool = True, description: str = ""
) -> None:
    """Vote for a topic "name", you can unvote if validate is false.
    The first player to vote must provide a description"""

    m, h = findHandler(name)

    if m is None:
        raise HTTPException(httpstatus.HTTP_403_FORBIDDEN, "Invalid vote type")

    uid = player.sessionName
    curVote = getVarName("vote_" + name, uid)
    async with getRedis().client() as conn:
        # Sanity checks
        if not await isPlayerValid(conn, player.sessionName, player.id, player.secret):
            raise HTTPException(httpstatus.HTTP_403_FORBIDDEN, "Invalid request")

        vip = getVarName(VOTE_IN_PROGRESS, uid)
        if not await conn.exists(curVote):
            if await conn.exists(vip):
                raise HTTPException(
                    httpstatus.HTTP_403_FORBIDDEN, "A vote is already in progress"
                )
            await publishEvent(
                uid, conn, cat="voteStart", name=name, description=description
            )

        # add player as "voted"
        await conn.sadd(vip, player.id)

        # add player's vote
        if validate:
            await conn.sadd(curVote, player.id)
        else:
            await conn.srem(curVote, player.id)

        # check if everybody voted
        await _checkVoteEnd(conn, uid, name)


async def _checkVoteEnd(conn: redis.Redis, uid: str, name: str) -> None:
    # check if everybody voted
    vip = getVarName(VOTE_IN_PROGRESS, uid)
    curVote = getVarName("vote_" + name, uid)
    m, h = findHandler(name)

    votants = await conn.scard(vip)
    totPlayers = await conn.llen(getVarName(sessVar.playerOrder.name, uid))

    if votants == totPlayers:
        await conn.unlink(vip)
        accepted = await conn.scard(curVote)
        majority = accepted > (totPlayers / 2)
        await conn.delete(curVote)
        if majority:
            assert h
            assert m
            game = await getGameBySessionId(uid, conn)
            await game.votePassed(uid, name, conn)
            await h(conn, uid, m)
        await publishEvent(uid, conn, cat="voteEnd", name=name, result=majority)
