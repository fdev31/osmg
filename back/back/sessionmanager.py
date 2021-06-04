import time

from fastapi import HTTPException
from pydantic import BaseModel
from typing import List
import aioredis

from .utils import ODict

t0 = time.time()*1000
ctx = ODict(sessions=[])

GAME_DATA = 'gameData'

async def _getUniquePlayerId():
    pid = await getRedis().incr('count_players')
    return pid

async def _genUniqueId():
    pid = await getRedis().incr('count_session')
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
    creationTime: int

def _getSessionPrefix(uid):
    return 'S%s:'%uid

async def getSession(uid, client=None):
    " fetch session info from redis "
    pattern = _getSessionPrefix(uid) + "*"
    all_keys = []
    async with (client or getRedis().client()) as conn:
        cur = -1
        while cur:
            cur, keys = await conn.scan(cur, match=pattern)
            all_keys.extend(keys)

    o = {GAME_DATA: {}}
    players = {}
    with getRedis().client as conn:
        for key in all_keys:
            val = await conn.get(key)
            splitk = key.split(':')
            if len(splitk) == 2:
                o[splitk[1]] = val
            elif splitk[1] == GAME_DATA:
                o[splitk[2]] = splitk[3]
            else: # players
                if splitk[1] not in players:
                    players[splitk[1]] = {}
                players[splitk[1]][splitk[2]] = val

    o['players'] = list(players.values())
    return o

def getGameDataPrefix(uid):
    return 'S%s:%s:'%(uid, GAME_DATA)

async def makeSession():
    " Create a new emtpy session with no players "
    uid = await _genUniqueId()
    sess = Session(name = uid, players = [], creationTime=time.time())

    prefix = _getSessionPrefix(uid)
    with getRedis().client() as conn:
        await conn.set(prefix+'gameType', sess.gameType)
        await conn.set(prefix+'name', sess.name)
    return sess

async def addPlayer(player: newPlayer):
    " Add a player to an existing session "
    sess = await getSession(player.sessionName)
    for p in sess['players']:
        if p['name'] == player.name:
            raise HTTPException(503, "A player called %s already exists"%player.name)
    pidP = _getUniquePlayerId()
    player_info = player.dict()
    del player_info['sessionName']
    prefix = _getSessionPrefix(player.sessionName)

    pid = await pidP
    player_info['id'] = pid
    with getRedis().client() as conn:
        for name, value in player_info.items():
            await conn.set("%sP%d:%s"%(prefix, pid, name), value)

        sess = await getSession(player.sessionName, conn)
    return sess

def getRedis():
    return ctx['redis']

def init(app, config):
    ctx['redis'] = aioredis.from_url('redis://'+config.redis_server,  decode_responses=True)
    app.post('/session/new', response_model=Session)(makeSession)
    app.post('/session/join', response_model=Session)(addPlayer)
