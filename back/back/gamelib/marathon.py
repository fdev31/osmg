import json
import random
import logging
from back.sessionmanager import GAME_DATA

from fastapi import HTTPException

from typing import List
from back.models import PlayerIdentifier
from back.globalHandlers import getRedis, getGameDataPrefix, publishEvent

GAME_NAME = "marathon"
logger = logging.getLogger(GAME_NAME)

async def throwDice(player: PlayerIdentifier, value: int) -> List[int]:
    """ Throw a number of dices """
    redis = getRedis()
    prefix = getGameDataPrefix(player.sessionName, player.id)
    propName = prefix + "_diceValue"

    dices = [random.randint(1, 6) for x in range(value)]
    async with redis.client() as conn:
        tmpDice = await conn.get(propName)
        if tmpDice:
            return HTTPException(503, "Dice already thrown")
        await conn.set(propName, json.dumps(dices))
    return dices

async def validateDice(player: PlayerIdentifier, value: str):
    """ Validate a previously thrown dice with a new order """
    redis = getRedis()
    prefix = getGameDataPrefix(player.sessionName, player.id)
    propName = prefix + "_diceValue"
    newVal = None
    async with redis.client() as conn:
        previous = json.loads(await conn.get(propName))
        current = [int(x) for x in value]
        try:
            for c in current:
                previous.remove(c)
        except ValueError:
            return HTTPException(503, "Dice not matching")
        await conn.delete(propName)
        propName = prefix + "diceValue"
        newVal = await conn.decrby(propName, int(value))
        logger.debug(f"{player} decr dice by {value}, it's now {newVal}")
        await publishEvent(player.sessionName, conn, cat="varUpdate", var="diceValue", val=newVal, player=player.id)
    return {"diceValue": newVal}

class DiceInterface:

    name = GAME_NAME
    description = "A multi-player maraton-like dice game"

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
    }

definition = {GAME_NAME: DiceInterface}
