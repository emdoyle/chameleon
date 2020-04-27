import logging
from typing import Dict
from src.db import (
    Session,
)
from src.services.game_state import GameStateService
from src.settings import LOGGER_NAME
from .base import BaseMessageHandler
from ..data import OutgoingMessages

logger = logging.getLogger(LOGGER_NAME)


class RestartMessageHandler(BaseMessageHandler):
    def handle(self, message: Dict, session: 'Session') -> 'OutgoingMessages':
        if message['kind'] != 'restart':  # TODO: constants
            raise ValueError("RestartMessageHandler expects messages of kind 'restart'")

        try:
            restart_state = message['restart']
        except KeyError:
            raise ValueError("Malformed message sent to ReadyMessageHandler")

        game_state_service = GameStateService(db_session=self.db_session)
        game_state_service.set_restart_state(
            session_id=session.id, game_id=session.game_id, restart_state=restart_state
        )
        restart_states = game_state_service.restart_states_for_game(game_id=session.game_id)
        logger.debug('Restart states: %s', restart_states)
        reset = False

        if all((value for key, value in restart_states.items())):
            self._handle_full_restart(session.game_id)
            reset = True

        return self._default_messages(game_id=session.game_id, reset=reset)

    def _handle_full_restart(self, game_id: int) -> None:
        game_state_service = GameStateService(db_session=self.db_session)
        game_state_service.start_new_round(game_id=game_id)
