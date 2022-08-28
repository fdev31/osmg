#!.tox/venv/bin/python
import importlib
from typing import Any
from back.games import GAMES
from json import dumps

OUT = "src/lib/gamelist.js"

gameDB: dict[str, dict[str, Any]] = {}

for game in GAMES:
    mod = importlib.import_module(f"back.gamelib.{game}")
    for gameName, api in mod.definition.items():
        print(game, "=>", gameName)
        gameDB[gameName] = api.info()

open(OUT, "w").write("export const gamelist = " + dumps(gameDB))
