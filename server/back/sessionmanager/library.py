import logging
from typing import Tuple, Any

from ..models import Session

logger = logging.getLogger("library")

games = {}


def registerGame(name, iface):
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


def getGameInitialData(gameType) -> dict[str, Any]:
    return games[gameType].getGameData()
