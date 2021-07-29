import time
import logging

from ..globalHandlers import getRedis

logger = logging.getLogger("Session")

t0 = time.time() * 1000


async def getUniquePlayerId() -> int:
    pid = await getRedis().incr("count_players")
    return pid


async def genUniqueSessionId() -> str:
    pid = await getRedis().incr("count_session")
    return hex(int("%d%d" % (pid, (time.time() * 1000) - t0)))[2:]


async def removeSession(sessionName: str, conn):
    " Delete all traces of a session " ""
    all_keys = []
    cur = b"0"
    while cur:
        cur, keys = await conn.scan(cur, match=f"S{sessionName}:*")
        all_keys.extend(keys)
    if all_keys:
        logger.info("Unlinking %s", keys)
        await conn.unlink(*all_keys)
