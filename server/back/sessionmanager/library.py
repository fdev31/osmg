import logging
from typing import Any, Tuple

from ..gamelib.interfaces import GameInterface
from ..models import Session

logger = logging.getLogger("library")

games = {}


def registerGame(name: str, iface: GameInterface) -> None:
    games[name] = iface


def getPlayerInitialData(
    sess: Session,
) -> Tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Returns tree list of (key, value) items:
    - simple props
    - lists
    - sets
    """
    game = games[sess.gameType]
    props = game.getPlayerData(sess)

    pdl = game.getPlayerDataLists(sess)
    lists = {li: props[li] for li in pdl}
    pds = game.getPlayerDataSets(sess)
    sets = {li: props[li] for li in pds}
    for name in lists.keys():
        del props[name]
    for name in sets.keys():
        del props[name]
    return (props, lists, sets)


def getGameInitialData(
    gameType: str,
) -> Tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Returns tree list of (key, value) items:
    - simple props
    - lists
    - sets
    """
    game = games[gameType]
    props = game.getGameData()

    pdl = game.getGameDataLists()
    lists = {li: props[li] for li in pdl}
    pds = game.getGameDataSets()
    sets = {li: props[li] for li in pds}
    for name in lists.keys():
        del props[name]
    for name in sets.keys():
        del props[name]
    return (props, lists, sets)
