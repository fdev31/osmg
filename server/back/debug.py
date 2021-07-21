import asyncio
import aioredis

from .globalHandlers import getRedis

async def getAllData():
    sessions = {}
    name = '*'
    if name[0] == 'S':
        name = name[1:]
    async with getRedis().client() as conn:
        cur = b"0"
        # collect data
        while cur:
            cur, keys = await conn.scan(cur, match=f"S{name}:*")
            for key in keys:
                try:
                    val = await conn.get(key)
                except aioredis.exceptions.ResponseError:
                    try:
                        val = await conn.smembers(key)
                    except aioredis.exceptions.ResponseError as e:
                        val = await conn.lrange(key, 0, -1)
                splitk = key.split(':')
                if splitk[0] not in sessions:
                    sessions[splitk[0]] = {}
                o = sessions[splitk[0]]
                if len(splitk) == 2:
                    o[splitk[1]] = val
                elif splitk[1] == 'g':
                    if 'game_data' not in o:
                        o['game_data'] = {}
                    o['game_data'][splitk[2]] = val
                else: # players
                    if 'players' not in o:
                        o['players'] = {}
                        o['players_data'] = {}

                    if splitk[1] not in o['players']:
                        o['players'][splitk[1]] = {}
                        o['players_data'][splitk[1]] = {}
                    if splitk[2] == 'g': # players data
                        o['players_data'][splitk[1]][splitk[3]] = val
                    else:
                        o['players'][splitk[1]][splitk[2]] = val
    return sessions

def showPlayersInfo(title, pi):
    if title:
        print(title)
    for name, info in sorted(pi.items()):
        print(f'     - {name:14} : {info}')


def init(app, config):
    app.get("/debug/getAll")(getAllData)
