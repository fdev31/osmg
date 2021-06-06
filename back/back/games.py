import importlib
import logging

from back.sessionmanager import registerGame

logger = logging.getLogger()

GAMES = ['maraton']

def init(app, config):
    for game in GAMES:
        logger.info(f"Game {game}")
        mod = importlib.import_module(f'back.gamelib.{game}')
        for gameName, api in mod.definition.items():
            registerGame(gameName, api)
            for actionName in api.actions:
                logger.debug(f"importing {game} action: {actionName}")
                app.post(f'/game/{gameName}/{actionName}')(api.actions[actionName])
