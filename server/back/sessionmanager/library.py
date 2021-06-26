games = {}

def registerGame(name, iface):
    games[name] = iface

def getPlayerInitialData(gameType):
    return games[gameType].getPlayerData().items()

def getGameInitialData(gameType):
    return games[gameType].getGameData().items()

