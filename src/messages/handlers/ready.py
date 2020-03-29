import random
import logging
from typing import Dict, Tuple, Set, List, TYPE_CHECKING
from src.db import (
    SetUpPhase,
    Round
)
from src.categories import (
    CATEGORIES
)
from .base import BaseMessageHandler
from ..data import OutgoingMessages

if TYPE_CHECKING:
    from src.db import (
        Session
    )

logger = logging.getLogger('chameleon')


class ReadyMessageHandler(BaseMessageHandler):
    def handle(self, message: Dict, session: 'Session') -> 'OutgoingMessages':
        if message['kind'] != 'ready':  # TODO: constants
            raise ValueError("ReadyMessageHandler expects messages of kind 'ready'")

        try:
            ready_state = message['ready']
        except KeyError:
            raise ValueError("Malformed message sent to ReadyMessageHandler")

        self.ready_states[session.id] = ready_state
        logger.debug('Ready states: %s', self.ready_states)
        filter_self = True
        session_ids = {
            session.id
            for session in self._get_sessions_in_game(game_id=session.game_id)
        }
        if all((value for key, value in self.ready_states.items() if key in session_ids)):
            self._handle_full_ready(session.game_id, session_ids=session_ids)
            filter_self = False

        return self._default_messages(
            game_id=session.game_id,
            session_id=session.id,
            filter_self=filter_self,
        )

    def _handle_full_ready(self, game_id: int, session_ids: Set[int]) -> None:
        # TODO: cache this in thread
        set_up_phase = self.db_session.query(SetUpPhase).join(
            Round, SetUpPhase.round_id == Round.id
        ).filter(
            Round.game_id == game_id
        ).first()
        if set_up_phase is None:
            raise ValueError("Could not find game to send full ready message!")

        dice_rolls = self._pick_dice_rolls()
        set_up_phase.category = self._pick_category()
        set_up_phase.big_die_roll = dice_rolls[0]
        set_up_phase.small_die_roll = dice_rolls[1]
        set_up_phase.chameleon_session_id = self._pick_chameleon(session_ids)
        set_up_phase.session_ordering = self._order_sessions(session_ids)
        self.db_session.add(set_up_phase)
        game_round = self.db_session.query(Round).filter(Round.id == set_up_phase.round_id).first()
        game_round.phase = 'clue'
        self.db_session.add(game_round)
        self.db_session.commit()

    def _order_sessions(self, sessions: Set[int]) -> List[int]:
        return random.sample(sessions, len(sessions))

    def _pick_category(self) -> str:
        category_choice = random.sample(CATEGORIES.keys(), 1)[0]
        logger.debug('Category chosen: %s', category_choice)
        return category_choice

    def _pick_dice_rolls(self) -> Tuple[int, int]:
        big = random.randint(1, 6)
        small = random.randint(1, 8)

        logger.debug('Big die: %s, Little die: %s', big, small)
        return big, small

    def _pick_chameleon(self, sessions: Set[int]) -> int:
        session_choice = random.sample(sessions, 1)[0]
        logger.debug('Session choice: %s', session_choice)
        return session_choice
