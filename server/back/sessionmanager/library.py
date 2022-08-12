from typing import Tuple, Any

games = {}


def registerGame(name, iface):
    games[name] = iface


def getPlayerInitialData(gameType) -> Tuple[Tuple[str, Any]]:
    """Returns tree list of (key, value) items:
    - simple props
    - lists
    - sets
    """
    game = games[gameType]
    props = game.getPlayerData()
    lists = {li: props[li] for li in game.getPlayerDataLists()}
    sets = {li: props[li] for li in game.getPlayerDataSets()}
    for name in lists.keys():
        del props[name]
    for name in sets.keys():
        del props[name]
    return (props.items(), lists.items(), sets.items())


def getGameInitialData(gameType):
    return games[gameType].getGameData().items()
