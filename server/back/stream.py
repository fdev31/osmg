import asyncio
import logging
from typing import Any, AsyncGenerator, Dict

import aioredis
from fastapi import FastAPI, WebSocket
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from .globalHandlers import getConfig
from .sessionmanager.public import connectPlayer, disconnectPlayer

logger = logging.getLogger("Stream")


async def sessionStreamSource(
    ws: WebSocket, topic: str, playerId: str
) -> AsyncGenerator[str, None]:

    channel: aioredis.client.PubSub = aioredis.from_url(
        "redis://" + getConfig().redis_server, decode_responses=True
    ).pubsub()
    await connectPlayer(topic, playerId)
    try:
        await channel.subscribe(topic)
        async for message in channel.listen():
            if message["type"] == "message":
                yield message["data"]
    except asyncio.CancelledError:
        await disconnectPlayer(topic, playerId)


async def gameEventStream(ws: WebSocket, topic: str, uid: str) -> None:
    "Returns an event source for the provided topic & user"
    logger.debug("New stream for %s @ %s", topic, uid)
    await ws.accept()
    try:
        async for event in sessionStreamSource(ws, topic, uid):
            await ws.send_text(event)
    except ConnectionClosedError:
        logger.debug("Stream disconnected")
        await disconnectPlayer(topic, uid)
    except ConnectionClosedOK:
        logger.debug("Stream disconnected OK")


def init(app: FastAPI, config: Dict[str, Any]) -> None:
    app.websocket("/c/stream")(gameEventStream)
