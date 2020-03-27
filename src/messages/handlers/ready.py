import random
import logging
from typing import Dict, Tuple, List, TYPE_CHECKING
from src.db import (
    SetUpPhase,
    Round
)
from .base import BaseMessageHandler
from ..data import OutgoingMessages, OutgoingMessage

if TYPE_CHECKING:
    from src.db import (
        Session
    )

logger = logging.getLogger('chameleon')


class ReadyMessageHandler(BaseMessageHandler):
    NORMAL_MESSAGE = OutgoingMessage(
        data={
            'assignment': 'normal'
        }
    )
    CHAMELEON_MESSAGE = OutgoingMessage(
        data={
            'assignment': 'chameleon'
        }
    )

    def handle(self, message: Dict, session: 'Session') -> 'OutgoingMessages':
        if message['kind'] != 'ready':  # TODO: constants
            raise ValueError("ReadyMessageHandler expects messages of kind 'ready'")

        try:
            ready_state = message['ready']
        except KeyError:
            raise ValueError("Malformed message sent to ReadyMessageHandler")

        self.ready_states[session.id] = ready_state
        if all(self.ready_states.values()):
            full_ready_messages = self._handle_full_ready(session.game_id)
        else:
            full_ready_messages = OutgoingMessages()

        return self._default_messages(game_id=session.game_id, session_id=session.id).merge(
            full_ready_messages
        )

    def _handle_full_ready(self, game_id: int) -> 'OutgoingMessages':
        # TODO: cache this in thread
        set_up_phase = self.db_session.query(SetUpPhase).join(
            Round, SetUpPhase.round_id == Round.id
        ).filter(
            Round.game_id == game_id
        ).first()
        if set_up_phase is None:
            raise ValueError("Could not find game to send full ready message!")

        session_ids_in_game = [
            session.id
            for session in self._get_sessions_in_game(game_id=game_id)
        ]
        dice_rolls = self._pick_dice_rolls()

        set_up_phase.category = self._pick_category()
        set_up_phase.big_die_roll = dice_rolls[0]
        set_up_phase.small_die_roll = dice_rolls[1]
        set_up_phase.chameleon_session_id = self._pick_chameleon(session_ids_in_game)
        self.db_session.add(set_up_phase)
        self.db_session.commit()

        return OutgoingMessages(
            messages={
                session_id: (
                    self.NORMAL_MESSAGE
                    if session_id != set_up_phase.chameleon_session_id
                    else self.CHAMELEON_MESSAGE
                )
                for session_id in session_ids_in_game
            }
        )

    def _pick_category(self) -> str:
        logger.debug('Category chosen: %s', 'default')
        return 'default'

    def _pick_dice_rolls(self) -> Tuple[int, int]:
        big = random.randint(1, 6)
        small = random.randint(1, 8)

        logger.debug('Big die: %s, Little die: %s', big, small)
        return big, small

    def _pick_chameleon(self, sessions: List[int]) -> int:
        session_choice = random.choice(sessions)
        logger.debug('Session choice: %s', session_choice)
        return session_choice
