import time
import logging
from typing import Awaitable

from ..globalHandlers import getRedis

from aioredis import Redis

logger = logging.getLogger("Session")

t0 = time.time() * 1000


async def getUniquePlayerId() -> int:
    pid = int(await getRedis().incr("count_players"))
    return pid


async def genUniqueSessionId() -> str:
    pid = await getRedis().incr("count_session")
    return hex(int("%d%d" % (pid, (time.time() * 1000) - t0)))[2:]


async def removeSession(sessionName: str, conn: Redis) -> None:
    " Delete all traces of a session " ""
    all_keys = []
    cur = 0
    while cur:
        cur, keys = await conn.scan(cur, match=f"S{sessionName}:*")
        all_keys.extend(keys)
    if all_keys:
        logger.info("Unlinking %s", keys)
        await conn.unlink(*all_keys)
