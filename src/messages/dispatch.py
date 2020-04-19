import logging
from typing import Dict, TYPE_CHECKING
from src.messages.handlers import (
    PlayerMessageHandler,
    VoteMessageHandler,
    ReadyMessageHandler,
    ClueMessageHandler,
    GuessMessageHandler,
    RestartMessageHandler,
)
from src.settings import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

if TYPE_CHECKING:
    from src.db import DBSession, Session
    from .data import OutgoingMessages


class MessageDispatch:
    HANDLERS = {
        'players': PlayerMessageHandler,
        'ready': ReadyMessageHandler,
        'vote': VoteMessageHandler,
        'clue': ClueMessageHandler,
        'guess': GuessMessageHandler,
        'restart': RestartMessageHandler,
    }

    def __init__(
            self,
            db_session: 'DBSession',
            game_id: int
    ):
        self.db_session = db_session
        self.game_id = game_id

    @classmethod
    def factory(
            cls,
            db_session: 'DBSession',
            game_id: int
    ) -> 'MessageDispatch':
        return cls(
            db_session=db_session,  # TODO: sorta weird how this is being passed around
            game_id=game_id
        )

    def handle(
            self,
            message: Dict,
            session: 'Session'
    ) -> 'OutgoingMessages':
        try:
            kind = message['kind']
        except KeyError:
            # TODO: custom exception
            raise

        return self.HANDLERS[kind].factory(
            db_session=self.db_session,
            game_id=self.game_id
        ).handle(
            message=message,
            session=session
        )
