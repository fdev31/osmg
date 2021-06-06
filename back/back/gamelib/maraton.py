import json
import random

from fastapi import HTTPException

from typing import List
from back.models import newPlayer, Session
from back.sessionmanager import getSession
from back.globalHandlers import getRedis, getGameDataPrefix

async def throwDice(player: newPlayer, value: int) -> List[int]:
    """ Throw a number of dices """
    redis = getRedis()
    prefix = getGameDataPrefix(newPlayer.sessionName, newPlayer.id)
    propName = "%s:_diceValue"%(prefix)

    dices = [random.randint(1, 6) for x in range(value)]
    with redis.client() as conn:
        tmpDice = int(await conn.get(propName))
        if tmpDice:
            return HTTPException(503, "Dice already thrown")
        await conn.set(propName, dices)
    return dices


async def validateDice(player: newPlayer, value: str):
    """ Validate a previously thrown dice with a new order """
    redis = getRedis()
    prefix = getGameDataPrefix(newPlayer.sessionName, newPlayer.id)
    propName = "%s:_diceValue"%(prefix)
    newVal = None
    with redis.client() as conn:
        previous = await conn.get(propName)
        current = [int(x) for x in value]
        try:
            for c in current:
                previous.remove(c)
        except ValueError:
            return HTTPException(503, "Dice not matching")
        await conn.set(propName, 0)
        propName = "%s:diceValue" % (prefix)
        await conn.decrby(propName, int(value))
        newVal = await conn.get(propName)
    return {"diceValue": newVal}


class DiceInterface:
    @staticmethod
    def getPlayerData():
        return dict(diceValue=2040, turn=0)

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

definition = {'dice': DiceInterface}
