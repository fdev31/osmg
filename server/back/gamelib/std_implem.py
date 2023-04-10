from typing import Any

from ..globalHandlers import publishEvent
from ..models import SESSION_GAME_DATA, SESSION_PLAYERS_DATA, Player, Session
from .interfaces import Events


async def def_playerAdded(sess: Session, player: Player) -> None:
    sid = str(player.id)
    extra: dict[str, Any] = {
        SESSION_PLAYERS_DATA: {sid: sess.playersData[sid]},
        SESSION_GAME_DATA: sess.gameData,
    }
    await publishEvent(
        sess.name, None, cat=Events.newPlayer.name, id=sid, name=player.name, **extra
    )
