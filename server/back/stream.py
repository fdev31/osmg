import logging
import asyncio
from  websockets.exceptions import ConnectionClosedError, ConnectionClosedOK


from fastapi import WebSocket
import aioredis

from .sessionmanager.public import connectPlayer, disconnectPlayer
from .globalHandlers import getConfig


logger = logging.getLogger("Stream")


async def sessionStreamSource(request, topic, playerId):

    channel = aioredis.from_url("redis://" + getConfig().redis_server, decode_responses=True).pubsub()
    await connectPlayer(topic, playerId)
    try:
        await channel.subscribe(topic)
        async for message in channel.listen():
            if message["type"] == "message":
                yield message["data"]
    except asyncio.CancelledError as e:
        await disconnectPlayer(topic, playerId)


async def gameEventStream(
    ws: WebSocket, topic: str, uid: str
):
    "Returns an event source for the provided topic & user"
    logger.debug("New stream for %s @ %s", topic, uid)
    await ws.accept()
    try :
        async for event in sessionStreamSource(ws , topic , uid ) :
            await ws.send_text(event)
    except ConnectionClosedError:
        logger.debug("Stream disconnected")
        await disconnectPlayer(topic, uid)
    except ConnectionClosedOK:
        logger.debug("Stream disconnected OK")

def init(app, config):
    app.websocket("/c/stream")(gameEventStream)
