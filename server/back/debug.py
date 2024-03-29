from typing import Any, Dict

import redis.asyncio as redis
from fastapi import FastAPI

from .globalHandlers import getRedis
from .utils import ODict


async def getAllData() -> Dict[str, Dict[str, Any]]:
    """Returns a database dump (SLOW! DO NOT USE IN PRODUCTION)"""
    sessions: Dict[str, Dict[str, Any]] = {}
    async with getRedis().client() as conn:
        async for key in conn.scan_iter(match="S*"):
            # collect data
            try:
                val = await conn.get(key)
            except redis.exceptions.ResponseError:
                try:
                    val = await conn.smembers(key)
                except redis.exceptions.ResponseError:
                    val = await conn.lrange(key, 0, -1)
            splitk = key.split(":")
            if splitk[0] not in sessions:
                sessions[splitk[0]] = {}
            o = sessions[splitk[0]]
            if len(splitk) == 2:
                o[splitk[1]] = val
            elif splitk[1] == "g":
                if "game_data" not in o:
                    o["game_data"] = {}
                o["game_data"][splitk[2]] = val
            else:  # players
                if "players" not in o:
                    o["players"] = {}
                    o["players_data"] = {}

                if splitk[1] not in o["players"]:
                    o["players"][splitk[1]] = {}
                    o["players_data"][splitk[1]] = {}
                if splitk[2] == "g":  # players data
                    o["players_data"][splitk[1]][splitk[3]] = val
                else:
                    o["players"][splitk[1]][splitk[2]] = val
    return {
        "sessions": sessions,
        "_info": {
            "tot_sessions": await conn.get("count_session"),
            "tot_players": await conn.get("count_players"),
        },
    }


def init(app: FastAPI, config: ODict) -> None:
    app.get("/debug/getAll")(getAllData)
