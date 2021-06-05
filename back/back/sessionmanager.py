import time
import asyncio
import logging
logger = logging.getLogger("Session")

from fastapi import HTTPException, Request
import aioredis
# SSE
#from fastapi_plugins import depends_redis, redis_plugin
from sse_starlette.sse import EventSourceResponse

from .utils import ODict
from .models import Player, newPlayer, Session

t0 = time.time()*1000
ctx = ODict(sessions=[])

GAME_DATA = 'gameData'

async def _getUniquePlayerId():
    pid = await getRedis().incr('count_players')
    return pid

async def _genUniqueId():
    pid = await getRedis().incr('count_session')
    return hex(int("%d%d"%(pid, (time.time()*1000)-t0)))[2:]


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

def getGameDataPrefix(uid, playerId=None):
    if playerId:
        return 'S%s:%s:P%s' % (uid, GAME_DATA, playerId)
    return 'S%s:%s:'%(uid, GAME_DATA)

async def makeSession():
    " Create a new emtpy session with no players "
    uid = await _genUniqueId()
    sess = Session(name = uid, players = [], creationTime=time.time())

    prefix = _getSessionPrefix(uid)
    with getRedis().client() as conn:
        #await conn.publish('sessionNameHere', 'pifou!')
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
    print("REDIS", ctx['redis'])
    return ctx['redis']

# async def on_startup() -> None:
#     print("Startup")
#     await redis_plugin.init_app(ctx.app)
#     await redis_plugin.init()

# async def on_shutdown() -> None:
#     await redis_plugin.terminate()

# https://medium.com/deepdesk/server-sent-events-in-fastapi-using-redis-pub-sub-eba1dbfe8031

async def event_source(request, params):
    channel = getRedis().pubsub()
    await channel.subscribe(params)
    async for message in channel.listen():
        if await request.is_disconnected():
            logger.debug('Request disconnected')
            break
        if message['type'] == 'message':
            yield {
                    "event": "Blah",
                    "data": message['data'],
            }
        #await asyncio.sleep(1)

async def eventStream(param: str, request: Request):
    return EventSourceResponse(event_source(request, param))


def init(app, config):
    ctx.app = app
    ctx['redis'] = aioredis.from_url('redis://'+config.redis_server,  decode_responses=True)
    app.post('/session/new', response_model=Session)(makeSession)
    app.post('/session/join', response_model=Session)(addPlayer)
    app.get('/stream')(eventStream)

#     app.on_event("startup")(on_startup)
#     app.on_event("shutdown")(on_shutdown)

