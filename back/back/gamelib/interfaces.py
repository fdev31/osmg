class GameInterface:

    name = "Unknown game"
    description = "No description yet"
    min_players = None
    max_players = None

    @classmethod
    def info(kls):
        return {
            "name": kls.name,
            "description": kls.description,
            "max_p": kls.max_players,
            "min_p": kls.min_players,
        }

    @staticmethod
    def getPlayerData():
        return {}

    @staticmethod
    def getGameData():
        return {}

    actions = {}

    @classmethod
    def definition(kls):
        return {kls.name: kls}
