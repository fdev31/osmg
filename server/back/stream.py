import asyncio
import logging
from typing import Any, AsyncGenerator, Dict

import aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .globalHandlers import getRedis
from .sessionmanager.public import connectPlayer, disconnectPlayer

logger = logging.getLogger("Stream")


async def sessionStreamSource(
    ws: WebSocket, topic: str, playerId: str
) -> AsyncGenerator[str, None]:

    channel: aioredis.client.PubSub = getRedis().pubsub()
    await connectPlayer(topic, playerId)
    try:
        await channel.subscribe(topic)
        async for message in channel.listen():
            if message["type"] == "message":
                yield message["data"]
    except asyncio.CancelledError as e:
        return


async def wait_for_disconnect(ws: WebSocket) -> None:
    """The second return value bolean will return True if the client disconnected"""
    try:
        await ws.receive_text()
    except WebSocketDisconnect as e:
        return


async def publish_events(ws: WebSocket, topic: str, uid: str) -> None:
    try:
        async for event in sessionStreamSource(ws, topic, uid):
            await ws.send_text(event)
    except Exception as e:
        logger.error(f"Exception occurred: {e}, DISCONNECT")


async def gameEventStream(ws: WebSocket, topic: str, uid: str) -> None:
    "Returns an event source for the provided topic & user"
    logger.debug("New stream for %s @ %s", uid, topic)
    await ws.accept()
    waitDisconnect = wait_for_disconnect(ws)
    streamTask = publish_events(ws, topic, uid)
    done, pending = await asyncio.wait(
        [waitDisconnect, streamTask], return_when=asyncio.FIRST_COMPLETED
    )
    done.pop()
    while len(pending) > 0:
        # cancel the other tasks in the waiter
        pending_task = pending.pop()
        pending_task.cancel()

    await disconnectPlayer(topic, uid)


def init(app: FastAPI, _config: Dict[str, Any]) -> None:
    app.websocket("/c/stream")(gameEventStream)
