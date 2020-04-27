from typing import Dict, TYPE_CHECKING
from .base import BaseMessageHandler
from ..data import OutgoingMessages

if TYPE_CHECKING:
    from src.db import (
        Session
    )


class PlayerMessageHandler(BaseMessageHandler):
    def handle(self, message: Dict, session: 'Session') -> 'OutgoingMessages':
        if message['kind'] != 'players':
            raise ValueError("PlayerMessageHandler expects messages of kind 'players'")

        return self._default_messages(game_id=session.game_id)
