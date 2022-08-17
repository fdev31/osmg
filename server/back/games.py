import importlib
import logging
from typing import Any, Dict

from fastapi import FastAPI

from .sessionmanager.library import registerGame

logger = logging.getLogger("games")

GAMES = ["marathon", "mock1", "atakks"]

gameDB: Dict[str, Dict[str, Any]] = {}


def listGames() -> dict[str, Any]:
    "list all games by name"
    return gameDB


def init(app: FastAPI, config: Dict[str, Any]) -> None:
    app.get("/c/gamelist", response_model=Dict)(listGames)

    for game in GAMES:
        logger.info(f"Game {game}")
        mod = importlib.import_module(f"back.gamelib.{game}")
        for gameName, api in mod.definition.items():
            gameDB[gameName] = api.info()
            logger.debug(f"processing {gameName}...")
            registerGame(gameName, api)
            for actionName in api.actions:
                logger.debug(f"importing {game} action: {actionName}")
                handler = api.actions[actionName]
                if hasattr(handler, "items"):  # this is a dict
                    properties = handler
                    handler = properties.pop("handler")
                else:
                    properties = {}
                app.post(f"/g/{gameName}/{actionName}", **properties)(handler)
