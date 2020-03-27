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

        # TODO: any other messages like this?
        # TODO: need to tell a player about cham status individually!

        full_game_state_message = self.message_builder.create_full_game_state_message(
            session_id=session.id, game_id=session.game_id
        )
        return OutgoingMessages(
            messages={
                session_in_game.id: [full_game_state_message]
                for session_in_game in self._get_sessions_in_game(session.game_id)
                if session_in_game.id != session.id
            }
        )
