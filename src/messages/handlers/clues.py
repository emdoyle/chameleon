import logging
from typing import Dict, TYPE_CHECKING
from src.settings import LOGGER_NAME
from .base import BaseMessageHandler

if TYPE_CHECKING:
    from src.db import (
        Session
    )
    from ..data import OutgoingMessages

logger = logging.getLogger(LOGGER_NAME)


class ClueMessageHandler(BaseMessageHandler):
    @classmethod
    def _validate_clue(cls, clue: str) -> bool:
        return ' ' not in clue

    def _update_game_state(self, session: 'Session', clue: str) -> None:
        clue_phase = self._get_clue_phase(session.game_id)
        clue_phase.clues = {**clue_phase.clues, str(session.id): clue}
        logger.debug("Clue phase clues are now: %s", clue_phase.clues)
        self.db_session.add(clue_phase)

        logger.debug("Connected session keys: %s", self.connected_sessions)
        if {int(key) for key in clue_phase.clues.keys()} == self.connected_sessions:
            logger.debug("Everybody in game: %s has given a clue, moving to voting phase!", session.game_id)
            current_round = self._get_round(session.game_id)
            current_round.phase = 'vote'
            self.db_session.add(current_round)

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
        if self._validate_clue(clue):
            self._update_game_state(session, clue)
        return self._default_messages(game_id=session.game_id, session_id=session.id, filter_self=False)
