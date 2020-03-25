from typing import Dict, TYPE_CHECKING
from .base import BaseMessageHandler
from ..data import OutgoingMessages

if TYPE_CHECKING:
    from src.db import (
        Session
    )


class ReadyMessageHandler(BaseMessageHandler):
    def handle(self, message: Dict, session: 'Session') -> 'OutgoingMessages':
        if message['kind'] != 'ready':  # TODO: constants
            raise ValueError("ReadyMessageHandler expects messages of kind 'ready'")

        try:
            ready_state = message['ready']
        except KeyError:
            raise ValueError("Malformed message sent to ReadyMessageHandler")

        self.ready_states[session.id] = ready_state
        sessions_in_game = self._get_sessions_in_game(session.game_id)
        full_game_state_message = self.message_builder.create_full_game_state_message(
            session_id=session.id,
            game_id=session.game_id
        )  # inefficient
        return OutgoingMessages(
            messages={
                session_in_game.id: [full_game_state_message]
                for session_in_game in sessions_in_game
                if session_in_game.id != session.id
            }
        )
