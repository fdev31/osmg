import re
import logging
from collections.abc import Callable

from fastapi import HTTPException
from starlette import status as httpstatus

from back.models import PlayerIdentifier
from back.globalHandlers import getRedis, publishEvent, getVarName
from back.globalHandlers import PLAYERS_ORDER, PLAYERS_CONNECTED, PLAYERS_READY

from .public import getGameBySessionId, isPlayerValid

logger = logging.getLogger("SessionVote")

async def kickPlayer(conn, sessionId: str, match: re.Match):
    whom = match.groups()[0]
    await conn.lrem(getVarName(PLAYERS_ORDER, sessionId), 1, whom)
    await conn.srem(getVarName(PLAYERS_CONNECTED, sessionId), whom)
    await conn.srem(getVarName(PLAYERS_READY, sessionId), whom)

votesHandlers = {
    re.compile('kick_(.*)'): kickPlayer,
}

def findHandler(name: str) -> tuple[re.Match, Callable[[str, str, list]]]:
    for handler in votesHandlers:
        m = handler.match(name)
        if m:
            return (m, votesHandlers[handler])
    return (None, None)

async def vote(player: PlayerIdentifier, name: str, validate: bool = True, description: str = ''):
    """ Vote for a topic "name", you can unvote if validate is false.
    The first player to vote must provide a description """

    m, h = findHandler(name)
    VOTE_IN_PROGRESS = "_voteInProgress"

    if m is None:
        raise HTTPException(httpstatus.HTTP_403_FORBIDDEN, "Invalid vote type")

    uid = player.sessionName
    curVote = getVarName("vote_" + name, uid)
    async with getRedis().client() as conn:
        if not await isPlayerValid(conn, player.sessionName, player.id, player.secret):
            raise HTTPException(httpstatus.HTTP_403_FORBIDDEN, "Invalid request")

        vip = getVarName(VOTE_IN_PROGRESS, uid)
        if not await conn.exists(curVote):
            if await conn.exists(vip):
                raise HTTPException(httpstatus.HTTP_403_FORBIDDEN, "A vote is already in progress")
            await publishEvent(uid, conn, cat="voteStart", name=name, description=description)

        conn.sadd(vip, player.id)

        if validate:
            await conn.sadd(curVote, player.id)
        else:
            await conn.srem(curVote, player.id)

        votants = await conn.scard(vip)
        totPlayers = await conn.llen(getVarName(PLAYERS_ORDER, uid))

        if votants == totPlayers:
            accepted = await conn.scard(curVote)
            if accepted > (totPlayers/2):
                await publishEvent(uid, conn, cat="voteEnd", name=name)
                await conn.delete(curVote)

                await h(conn, uid, m)
                conn.unlink(vip)
                game = await getGameBySessionId(uid, conn)
                await game.votePassed(uid, name, conn)
