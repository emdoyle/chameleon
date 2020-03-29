import logging
from abc import ABC, abstractmethod
from typing import Dict, Iterable, Optional, TYPE_CHECKING
from sqlalchemy.sql.expression import false
from src.db import (
    Session, Game, Round, SetUpPhase
)
from src.messages.builder import MessageBuilder
from ..data import OutgoingMessages

if TYPE_CHECKING:
    from src.server import GameStateHandler
    from src.db import (
        DBSession
    )

logger = logging.getLogger('chameleon')


class AbstractMessageHandler(ABC):
    @classmethod
    @abstractmethod
    def factory(
            cls,
            db_session: 'DBSession',
            ready_states: Dict[int, bool],
            connected_sessions: Dict[int, 'GameStateHandler'],
    ):
        ...

    @abstractmethod
    def handle(self, message: Dict, session: 'Session') -> 'OutgoingMessages':
        ...


class BaseMessageHandler(AbstractMessageHandler):
    def __init__(
            self,
            db_session: 'DBSession',
            ready_states: Dict[int, bool],
            connected_sessions: Dict[int, 'GameStateHandler']
    ):
        self.db_session = db_session
        self.ready_states = ready_states
        self.message_builder = MessageBuilder.factory(
            db_session=db_session,
            ready_states=ready_states,
            connected_sessions=connected_sessions
        )

    @classmethod
    def factory(
            cls,
            db_session: 'DBSession',
            ready_states: Dict[int, bool],
            connected_sessions: Dict[int, 'GameStateHandler'],
    ):
        return cls(db_session=db_session, ready_states=ready_states, connected_sessions=connected_sessions)

    def _get_sessions_in_game(self, game_id: int) -> Iterable['Session']:
        return self.db_session.query(Session).filter(Session.game_id == game_id).all()

    def _get_chameleon_session_id(self, game_id: int) -> Optional[int]:
        set_up_phase = self.db_session.query(SetUpPhase).join(
            Round, Round.id == SetUpPhase.round_id
        ).join(
            Game, Game.id == Round.game_id
        ).filter(
            Round.completed == false()
        ).filter(
            Game.id == game_id
        ).first()
        if set_up_phase is None:
            logger.debug("Tried to get chameleon session id but none found with game id: %s", game_id)
            return None
        return set_up_phase.chameleon_session_id

    def _default_messages(self, game_id: int, session_id: int, filter_self: bool = True) -> 'OutgoingMessages':
        sessions_in_game = self._get_sessions_in_game(game_id)
        chameleon_session_id = self._get_chameleon_session_id(game_id)
        full_game_state_message = self.message_builder.create_full_game_state_message(
            game_id=game_id
        )  # inefficient

        messages = {}
        for session_in_game in sessions_in_game:
            if filter_self and session_in_game.id == session_id:
                continue
            if chameleon_session_id is not None and session_in_game.id == chameleon_session_id:
                logger.debug("Showing session %s that they are the chameleon!", session_in_game.id)
                messages[session_in_game.id] = [full_game_state_message.add_chameleon()]
            else:
                messages[session_in_game.id] = [full_game_state_message]
        return OutgoingMessages(messages=messages)
