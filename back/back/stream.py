import logging

from fastapi import Request
from sse_starlette.sse import EventSourceResponse

from back.models import PlayerIdentifier
from back.sessionmanager import disconnectPlayer
from back.globalHandlers import getRedis

logger = logging.getLogger("Stream")

async def event_source(request, params, playerId):
    channel = getRedis().pubsub()
    await channel.subscribe(params)
    async for message in channel.listen():
        if await request.is_disconnected():
            await disconnectPlayer(playerId)
            logger.debug('Stream disconnected')
            break
        if message['type'] == 'message':
            yield {
                "event": "update",
                "data": message['data'],
            }

async def eventStream(request: Request, player: PlayerIdentifier) -> EventSourceResponse:
    " Returns an event source for the provided topic & user "
    return EventSourceResponse(event_source(request, topic, player.id))

def init(app, config):
    app.get('/stream')(eventStream)
