import json
import time
import random
import logging
from typing import List

from fastapi import HTTPException
from starlette import status as httpstatus

from back.gamelib.interfaces import GameInterface
from back.sessionmanager import GAME_DATA
from back.models import PlayerIdentifier
from back.globalHandlers import getRedis, getSessionPrefix, getGameDataPrefix, publishEvent
from .interfaces import GameInterface

async def startGame(player: PlayerIdentifier):
    " Notifies that some player is ready to start the game "
    redis = getRedis()
    prefix = getGameDataPrefix(player.sessionName)
    async with redis.client() as conn:
        pr = prefix+'playersReady'
        if await conn.sismember(pr, player.id):
            raise HTTPException(httpstatus.HTTP_409_CONFLICT, "Action already done")
        await publishEvent(player.sessionName, conn, cat="ready", player=player.id)
        await conn.sadd(pr, player.id)
        await conn.rpush(prefix+'playerOrder', player.id)
        nbPlayersReady = await conn.scard(pr)
        if nbPlayersReady == await conn.get(getSessionPrefix(player.sessionName)+'nbPlayers'):
             # all players are ready!
             await conn.set(f'S{player.sessionName}:startTime', int(time.time()))
             await publishEvent(player.sessionName, conn, cat="start", msg="game started")

async def isPlayerTurn(conn, prefix, playerId):
    print(prefix+"curPlayer")
    curPlayer = await conn.get(prefix+"curPlayer")
    curPlayerId = await conn.lindex(prefix+"playerOrder", int(curPlayer))
    return int(curPlayerId) == int(playerId)

async def throwDice(player: PlayerIdentifier) -> List[int]:
    """ Throw a number of dices (defined by the current player score) """
    redis = getRedis()
    gprefix = getGameDataPrefix(player.sessionName)
    prefix = getGameDataPrefix(player.sessionName, player.id)
    propName = prefix + "_diceValue"

    async with redis.client() as conn:
        if not await isPlayerTurn(conn, gprefix, player.id):
            raise HTTPException(httpstatus.HTTP_403_FORBIDDEN, "Not your turn!")
        tmpDice = await conn.get(propName)
        if tmpDice:
            raise HTTPException(httpstatus.HTTP_421_MISDIRECTED_REQUEST, "Dice already thrown")
        remainingDistance = await conn.get(prefix+'diceValue')

        dices = [random.randint(1, 6) for x in range(min(4, len(remainingDistance)))]
        await conn.set(propName, json.dumps(dices))
    return dices

async def validateDice(player: PlayerIdentifier, value: str):
    """ Validate a previously thrown dice with a new order """
    redis = getRedis()
    prefix = getGameDataPrefix(player.sessionName, player.id)
    g_prefix = getGameDataPrefix(player.sessionName)
    propName = prefix + "_diceValue"
    newVal = None
    async with redis.client() as conn:
        if not await isPlayerTurn(conn, g_prefix, player.id):
            raise HTTPException(httpstatus.HTTP_403_FORBIDDEN, "Not your turn!")
        previous = json.loads(await conn.get(propName))
        current = [int(x) for x in value]
        try:
            for c in current:
                previous.remove(c)
        except ValueError:
            raise HTTPException(httpstatus.HTTP_421_MISDIRECTED_REQUEST, "Dice not matching")
        await conn.delete(propName)
        propName = prefix + "diceValue"
        newVal = await conn.decrby(propName, int(value))
        logger.debug(f"{player} decr dice by {value}, it's now {newVal}")
        await publishEvent(player.sessionName, conn, cat="varUpdate", var="diceValue", val=newVal, player=player.id)

        nbPlayers = int(await conn.get(getSessionPrefix(player.sessionName)+"nbPlayers"))
        curPlayer = int(await conn.incr(g_prefix+"curPlayer"))

        if newVal == 0: # End of game
            await publishEvent(player.sessionName, conn, cat="endOfGame", message="We have a winner!", player=player.id)
        elif newVal < 0:
            await conn.sadd(g_prefix+"losers", player.id)
        else: # check if it's the last player
            nbLosers = int(await conn.scard(g_prefix+"losers"))
            if nbLosers == nbPlayers - 1:
                await publishEvent(player.sessionName, conn, cat="endOfGame", message="We have a winner!", player=player.id)

        if curPlayer >= nbPlayers:
            turn = await conn.incr(g_prefix + "turns")
            await publishEvent(player.sessionName, conn, cat="newTurn", val=turn)
            await conn.set(g_prefix + "curPlayer", 0)
            curPlayer = 0

        curPlayerId = await conn.lindex(g_prefix + "playerOrder", curPlayer)
        await publishEvent(player.sessionName, conn, cat="curPlayer", val=curPlayerId)

    return {"diceValue": newVal}

class DiceInterface(GameInterface):
    name = "marathon"
    description = "A multi-player maraton-like dice game"
    min_players = 2
    max_players = None

    @staticmethod
    def getPlayerData():
        return dict(diceValue=42195, turn=0)

    @staticmethod
    def getGameData():
        return {
            "turns": 0,
            "curPlayer": 0,
        }

    actions = {
        'throwDice': throwDice,
        'validateDice': validateDice,
        'start': startGame,
    }

logger = logging.getLogger(DiceInterface.name)

definition = DiceInterface.definition()
