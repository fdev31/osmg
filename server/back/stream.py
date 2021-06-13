import logging
import asyncio

from fastapi import Request
from sse_starlette.sse import EventSourceResponse

from back.models import PlayerIdentifier
from back.sessionmanager import connectPlayer, disconnectPlayer
from back.globalHandlers import getRedis

logger = logging.getLogger("Stream")

async def sessionStreamSource(request, topic, playerId):
    channel = getRedis().pubsub()
    await connectPlayer(topic, playerId)
    try:
        await channel.subscribe(topic)
        async for message in channel.listen():
            if await request.is_disconnected():
                logger.debug('Stream disconnected')
                await disconnectPlayer(topic, playerId)
                break
            if message['type'] == 'message':
                yield {
                    "event": "update",
                    "data": message['data'],
                }
    except asyncio.CancelledError as e:
        await disconnectPlayer(topic, playerId)

async def gameEventStream(request: Request, topic: str, uid: str) -> EventSourceResponse:
    " Returns an event source for the provided topic & user "
    return EventSourceResponse(sessionStreamSource(request, topic, uid))

def init(app, config):
    app.get('/stream')(gameEventStream)
