import logging
from typing import Dict, TYPE_CHECKING
from .base import BaseMessageHandler

if TYPE_CHECKING:
    from src.db import (
        Session
    )
    from ..data import OutgoingMessages

logger = logging.getLogger('chameleon')


class GuessMessageHandler(BaseMessageHandler):
    def _is_chameleon(self, session: 'Session') -> bool:
        return session.id == self._get_chameleon_session_id(session.game_id)

    def _check_guess(self, session: 'Session', guess: str) -> bool:
        ...

    def _update_game_state(self, session: 'Session', guess: str, guess_is_correct: bool) -> None:
        current_round = self._get_round(session.game_id)
        reveal_phase = current_round.reveal_phase
        reveal_phase.guess = guess
        if guess_is_correct:
            current_round.winner = "Chameleon"
        else:
            current_round.winner = "The People"
        self.db_session.add(current_round)
        self.db_session.add(reveal_phase)
        self.db_session.commit()

    def handle(self, message: Dict, session: 'Session') -> 'OutgoingMessages':
        if message['kind'] != 'guess':
            raise ValueError("GuessMessageHandler expects messages of kind 'guess'")

        if not self._is_chameleon(session):
            logger.error("Session %s is not the chameleon and should not submit a guess", session.id)
            return OutgoingMessages()

        try:
            guess = message['guess']
        except KeyError:
            raise ValueError("Guess message must contain a 'guess' key")

        self._update_game_state(session, guess, self._check_guess(session, guess))
        return self._default_messages(game_id=session.game_id, session_id=session.id, filter_self=False)
