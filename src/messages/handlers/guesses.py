import logging
from typing import Dict, TYPE_CHECKING
from src.categories import decode
from src.settings import LOGGER_NAME
from .base import BaseMessageHandler

if TYPE_CHECKING:
    from src.db import Session
    from ..data import OutgoingMessages

logger = logging.getLogger(LOGGER_NAME)


class GuessMessageHandler(BaseMessageHandler):
    def _is_chameleon(self, session: "Session") -> bool:
        return session.id == self._get_chameleon_session_id(session.game_id)

    def _check_guess(self, session: "Session", guess: str) -> bool:
        set_up_phase = self._get_set_up_phase(session.game_id)
        expected_answer = decode(
            category=set_up_phase.category,
            big_die_roll=set_up_phase.big_die_roll,
            small_die_roll=set_up_phase.small_die_roll,
        )
        return expected_answer is not None and expected_answer.lower() == guess.lower()

    def _update_game_state(
        self, session: "Session", guess: str, guess_is_correct: bool
    ) -> None:
        reveal_phase = self._get_reveal_phase(session.game_id)
        reveal_phase.guess = guess
        self.db_session.add(reveal_phase)
        self.db_session.commit()
        if guess_is_correct:
            self._update_game_ending(session.game_id, "The Chameleon")
        else:
            self._update_game_ending(session.game_id, "The People")

    def handle(self, message: Dict, session: "Session") -> "OutgoingMessages":
        if message["kind"] != "guess":
            raise ValueError("GuessMessageHandler expects messages of kind 'guess'")

        if not self._is_chameleon(session):
            logger.error(
                "Session %s is not the chameleon and should not submit a guess",
                session.id,
            )
            return OutgoingMessages()

        try:
            guess = message["guess"]
        except KeyError:
            raise ValueError("Guess message must contain a 'guess' key")

        self._update_game_state(session, guess, self._check_guess(session, guess))
        return self._default_messages(game_id=session.game_id)
