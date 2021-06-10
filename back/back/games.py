import importlib
import logging

from typing import Dict

from back.sessionmanager import registerGame

logger = logging.getLogger()

GAMES = ['marathon']

gameDB = {}

def listGames() -> dict:
    " list all games by name "
    return gameDB 

def init(app, config):
    app.get('/gamelist', response_model=Dict)(listGames)

    for game in GAMES:
        logger.info(f"Game {game}")
        mod = importlib.import_module(f'back.gamelib.{game}')
        for gameName, api in mod.definition.items():
            gameDB[gameName] = api.info()
            registerGame(gameName, api)
            for actionName in api.actions:
                logger.debug(f"importing {game} action: {actionName}")
                handler = api.actions[actionName]
                if hasattr(handler, 'items'): # this is a dict
                    properties = handler
                    handler = properties.pop('handler')
                else:
                    properties = {}
                app.post(f'/game/{gameName}/{actionName}', **properties)(handler)

