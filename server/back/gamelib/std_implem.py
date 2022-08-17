from .interfaces import Events
from ..models import SESSION_GAME_DATA, Session, Player, SESSION_PLAYERS_DATA
from ..globalHandlers import publishEvent


async def def_playerAdded(sess: Session, player: Player) -> None:
    sid = str(player.id)
    extra = {
        SESSION_PLAYERS_DATA: {sid: sess.playersData[sid]},
        SESSION_GAME_DATA: sess.gameData,
    }
    await publishEvent(
        sess.name, None, cat=Events.newPlayer.name, id=sid, name=player.name, **extra
    )
