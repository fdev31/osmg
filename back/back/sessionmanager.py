from fastapi import HTTPException
from itertools import count
import time
from pydantic import BaseModel
from typing import List

t0 = time.time()*1000

from .utils import ODict

import aioredis
ctx = ODict(sessions=[])
ctx_by_name = {}
ctxidGen = count()

async def _getUniquePlayerId():
    pid = await ctx.redis.incr('count_players')
    return pid

async def _genUniqueId():
    pid = await ctx.redis.incr('count_session')
    return hex(int("%d%d"%(pid, (time.time()*1000)-t0)))[2:]

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


def _getSessionPrefix(uid):
    return 'S%s_'%uid

async def getSession(uid):
    " fetch session info from redis "
    prefix = _getSessionPrefix(uid)
    all_keys = []
    async with ctx.redis.client() as conn:
        cur = b"0"  # set initial cursor to 0
        while cur:
            cur, keys = await conn.scan(cur, match=prefix+"*")
            all_keys.extend(keys)

    o = {'gameData': {}}
    players = {}
    for key in all_keys:
        val = await ctx.redis.get(key)
        splitk = key.split('_')
        if len(splitk) == 2:
            o[splitk[1]] = val
        elif splitk[1] == 'gameData':
            o[splitk[2]] = splitk[3]
        else: # players
            if splitk[1] not in players:
                players[splitk[1]] = {}
            players[splitk[1]][splitk[2]] = val

    o['players'] = list(players.values())
    return o


def getGameDataPrefix(uid):
    return 'S%s_gameData_'%uid

async def makeSession():
    " Create a new emtpy session with no players "
    uid = await _genUniqueId()
    sess = Session(
        players = [],
        name = uid)

    prefix = _getSessionPrefix(uid)
    await ctx.redis.set(prefix+'gameType', sess.gameType)
    await ctx.redis.set(prefix+'name', sess.name)
    
#    ctx.sessions.append(sess)
#    ctx_by_name[uid] = sess
    return sess

async def addPlayer(player: newPlayer):
    " Add a player to an existing session "
    sess = await getSession(player.sessionName)
    for p in sess['players']:
        if p['name'] == player.name:
            raise HTTPException(500, "A player called %s already exists"%player.name)
    player_info = player.dict()
    pid = await _getUniquePlayerId()
    player_info['id'] = pid
    del player_info['sessionName']
    prefix = _getSessionPrefix(player.sessionName)

    for name, value in player_info.items():
        await ctx.redis.set("%sP%d_%s"%(prefix, pid, name), value)

    sess = await getSession(player.sessionName)
    return sess

def getRedis():
    return ctx.redis

def init(app, config):
    ctx['redis'] = aioredis.from_url('redis://'+config.redis_server,  decode_responses=True)
    app.post('/session/new', response_model=Session)(makeSession)
    app.post('/session/join', response_model=Session)(addPlayer)
