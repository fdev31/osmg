import logging

from fastapi import Request
from sse_starlette.sse import EventSourceResponse

from back.sessionManager import disconnectPlayer
from back.globalHandlers import getRedis

logger = logging.getLogger("Stream")

async def event_source(request, params):
    channel = getRedis().pubsub()
    await channel.subscribe(params)
    async for message in channel.listen():
        if await request.is_disconnected():
            await disconnectPlayer()
            logger.debug('Request disconnected')
            break
        if message['type'] == 'message':
            yield {
                "event": "update",
                "data": message['data'],
            }

async def eventStream(topic: str, request: Request) -> EventSourceResponse:
    " Returns an event source for the provided topic "
    return EventSourceResponse(event_source(request, topic))

def init(app, config):
    app.get('/stream')(eventStream)
