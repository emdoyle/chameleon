from abc import ABC, abstractmethod
from typing import Dict, Iterable, TYPE_CHECKING
from src.db import (
    Session
)
from src.messages.builder import MessageBuilder
from ..data import OutgoingMessages

if TYPE_CHECKING:
    from tornado.websocket import WebSocketHandler
    from src.db import (
        DBSession
    )


class AbstractMessageHandler(ABC):
    @classmethod
    @abstractmethod
    def factory(
            cls,
            db_session: 'DBSession',
            ready_states: Dict[int, bool],
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
    ):
        self.db_session = db_session
        self.ready_states = ready_states
        self.message_builder = MessageBuilder.factory(
            db_session=db_session,
            ready_states=ready_states
        )

    @classmethod
    def factory(
            cls,
            db_session: 'DBSession',
            ready_states: Dict[int, bool],
    ):
        return cls(db_session=db_session, ready_states=ready_states)

    def _get_sessions_in_game(self, game_id: int) -> Iterable['Session']:
        return self.db_session.query(Session).filter(Session.game_id == game_id).all()

    def _default_messages(self, game_id: int, session_id: int) -> 'OutgoingMessages':
        sessions_in_game = self._get_sessions_in_game(game_id)
        full_game_state_message = self.message_builder.create_full_game_state_message(
            game_id=game_id
        )  # inefficient
        return OutgoingMessages(
            messages={
                session_in_game.id: [full_game_state_message]
                for session_in_game in sessions_in_game
                if session_in_game.id != session_id
            }
        )
