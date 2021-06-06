__all__ = ['getSession', 'registerGame']
import time
import logging
logger = logging.getLogger("Session")

from fastapi import HTTPException
import aioredis

from back.models import newPlayer, Session
from back.globalHandlers import getRedis, setRedis, publishEvent, getSessionPrefix

t0 = time.time()*1000

GAME_DATA = 'g'

async def _getUniquePlayerId():
    pid = await getRedis().incr('count_players')
    return pid

async def _genUniqueId():
    pid = await getRedis().incr('count_session')
    return hex(int("%d%d"%(pid, (time.time()*1000)-t0)))[2:]

async def getSession(uid, client=None):
    " fetch session info from redis "
    pattern = getSessionPrefix(uid) + "*"
    all_keys = []
    o = {GAME_DATA: {}}
    players = {}
    players_data = {}
    async with (client or getRedis().client()) as conn:
        cur = b"0"
        while cur:
            cur, keys = await conn.scan(cur, match=pattern)
            all_keys.extend(keys)

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
                    players_data[splitk[1]] = {}
                if splitk[2] == 'g': # players data
                    players_data[splitk[1]][splitk[3]] = val
                else:
                    players[splitk[1]][splitk[2]] = val

    o['players'] = list(players.values())
    o['playersData'] = players_data
    return o

async def makeSession() -> Session:
    " Create a new emtpy session with no players "
    uid = await _genUniqueId()
    sess = Session(name = uid, players = [], creationTime=int(time.time()))

    prefix = getSessionPrefix(uid)

    async with getRedis().client() as conn:

        for name, value in games[sess.gameType].getGameData().items():
            await conn.set("%s%s:%s"%(prefix, GAME_DATA, name), value)
            sess[name] = value

        for field in ('creationTime', 'name', 'gameType'):
            await conn.set(prefix+field, getattr(sess, field))
    return sess

games = {}
def registerGame(name, iface):
    games[name] = iface

async def addPlayer(player: newPlayer) -> Session:
    " Add a player to an existing session "
    sess = await getSession(player.sessionName)

    for p in sess['players']:
        if p['name'] == player.name:
            raise HTTPException(503, "A player called %s already exists"%player.name)

    pidP = _getUniquePlayerId()
    player_info = player.dict()
    del player_info['sessionName']
    prefix = getSessionPrefix(player.sessionName)

    pid = await pidP
    player_info['id'] = pid
    async with getRedis().client() as conn:
        for name, value in player_info.items():
            await conn.set("%sP%d:%s"%(prefix, pid, name), value)

        gameType = await conn.get(prefix+'gameType')
        for name, value in games[gameType].getPlayerData().items():
            await conn.set("%sP%d:g:%s"%(prefix, pid, name), value)

        pub = publishEvent(player.sessionName, None, cat='newPlayer', name=player.name, avatar=player.avatar)
        sess = await getSession(player.sessionName, conn)
        await pub
    return sess

def init(app, config):
    setRedis(aioredis.from_url('redis://'+config.redis_server,  decode_responses=True))
    app.post('/session/new', response_model=Session)(makeSession)
    app.post('/session/join', response_model=Session)(addPlayer)
