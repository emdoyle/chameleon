from abc import ABC, abstractmethod
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from tornado.websocket import WebSocketHandler
    from src.db import (
        DBSession,
        Session
    )
    from ..data import OutgoingMessages


class AbstractMessageHandler(ABC):
    @classmethod
    @abstractmethod
    def factory(
            cls,
            db_session: 'DBSession',
            ready_states: Dict[int, bool],
    ):
        ...

    @classmethod
    @abstractmethod
    def handle(cls, message: Dict, session: 'Session') -> 'OutgoingMessages':
        ...


class BaseMessageHandler(AbstractMessageHandler):
    def __init__(
            self,
            db_session: 'DBSession',
            ready_states: Dict[int, bool],
    ):
        self.db_session = db_session
        self.ready_states = ready_states

    @classmethod
    def factory(
            cls,
            db_session: 'DBSession',
            ready_states: Dict[int, bool],
    ):
        return cls(db_session=db_session, ready_states=ready_states)
