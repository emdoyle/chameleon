import logging
from typing import Dict, TYPE_CHECKING
from .base import BaseMessageHandler

if TYPE_CHECKING:
    from src.db import (
        Session
    )
    from ..data import OutgoingMessages

logger = logging.getLogger('chameleon')


class ClueMessageHandler(BaseMessageHandler):
    def _update_clues(self, session: 'Session', clue: str) -> None:
        clue_phase = self._get_clue_phase(session.game_id)
        clue_phase.clues = {**clue_phase.clues, session.id: clue}
        self.db_session.add(clue_phase)
        self.db_session.commit()

    def handle(self, message: Dict, session: 'Session') -> 'OutgoingMessages':
        if message['kind'] != 'clue':
            raise ValueError("ClueMessageHandler expects messages of kind 'clue'")

        clue_turn_session_id = self._get_clue_turn_session_id(game_id=session.game_id)
        if not session.id == clue_turn_session_id:
            logger.error("Received clue message from session %s but clue turn is %s", session.id, clue_turn_session_id)
            return OutgoingMessages()
        try:
            clue = message['clue']
        except KeyError:
            raise ValueError("Clue message must contain 'clue' key")
        self._update_clues(session, clue)
        return self._default_messages(game_id=session.game_id, session_id=session.id, filter_self=False)
