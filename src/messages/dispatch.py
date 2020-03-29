from typing import Dict, TYPE_CHECKING
from src.messages.handlers import (
    PlayerMessageHandler,
    VoteMessageHandler,
    ReadyMessageHandler,
    ClueMessageHandler,
    GuessMessageHandler
)

if TYPE_CHECKING:
    from src.server import GameStateHandler
    from src.db import (
        DBSession,
        Session
    )
    from .data import OutgoingMessages


class MessageDispatch:
    HANDLERS = {
        'players': PlayerMessageHandler,
        'ready': ReadyMessageHandler,
        'vote': VoteMessageHandler,
        'clue': ClueMessageHandler,
        'guess': GuessMessageHandler
    }

    @classmethod
    def handle(
            cls,
            message: Dict,
            db_session: 'DBSession',
            session: 'Session',
            ready_states: Dict[int, bool],
            connected_sessions: Dict[int, 'GameStateHandler']
    ) -> 'OutgoingMessages':
        try:
            kind = message['kind']
        except KeyError:
            # TODO: custom exception
            raise

        return cls.HANDLERS[kind].factory(
            db_session=db_session,
            ready_states=ready_states,
            connected_sessions=connected_sessions,
        ).handle(
            message=message,
            session=session
        )
