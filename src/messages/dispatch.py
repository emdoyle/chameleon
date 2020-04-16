import logging
from typing import Dict, Set, Optional, TYPE_CHECKING
from src.key_value import r
from src.messages.handlers import (
    PlayerMessageHandler,
    VoteMessageHandler,
    ReadyMessageHandler,
    ClueMessageHandler,
    GuessMessageHandler,
    RestartMessageHandler,
)
from src.db import Session, Game
from src.constants import READY_STATES_KEY, RESTART_STATES_KEY, CONNECTED_SESSIONS_KEY
from src.settings import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

if TYPE_CHECKING:
    from src.db import DBSession
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
            ready_states: Dict[int, bool],
            restart_states: Dict[int, bool],
            connected_sessions: Set[int],
    ):
        self.db_session = db_session
        self.ready_states = ready_states
        self.restart_states = restart_states
        self.connected_sessions = connected_sessions

    @classmethod
    def factory(
            cls,
            db_session: 'DBSession',
            game_id: int,
            ready_states: Optional[Dict[int, bool]] = None,
            restart_states: Optional[Dict[int, bool]] = None,
            connected_sessions: Optional[Set[int]] = None,
    ) -> 'MessageDispatch':
        if ready_states is None:
            ready_states = cls.ready_states_for_game(db_session, game_id)
        if restart_states is None:
            restart_states = cls.restart_states_for_game(db_session, game_id)
        if connected_sessions is None:
            connected_sessions = cls.connected_sessions_in_game(db_session, game_id)
        return cls(
            db_session=db_session,  # TODO: sorta weird how this is being passed around
            restart_states=restart_states,
            ready_states=ready_states,
            connected_sessions=connected_sessions
        )

    @classmethod
    def _session_ids_for_game(cls, db_session: 'DBSession', game_id: int) -> Set[int]:
        sessions_in_game = db_session.query(Session).join(Game, Game.id == Session.game_id).filter(
            Game.id == game_id
        ).all()
        return {session.id for session in sessions_in_game}

    @classmethod
    def ready_states_for_game(cls, db_session: 'DBSession', game_id: int) -> Dict[int, bool]:
        session_ids = cls._session_ids_for_game(db_session, game_id)
        r_pipe = r.pipeline()
        for session_id in session_ids:
            r_pipe.hget(f"{READY_STATES_KEY}:{str(game_id)}", str(session_id))
        ready_states = r_pipe.execute()
        # This is sensitive to ordering... make sure pipelining preserves ordering
        result = {
            session_id: bool(ready_state)
            for ready_state, session_id in zip(ready_states, session_ids)
        }
        logger.debug("Ready states in game %s are:\n%s", game_id, result)
        return result

    # TODO: really think about whether it is useful to check Redis (since sessions clear on DC)
    @classmethod
    def restart_states_for_game(cls, db_session: 'DBSession', game_id: int) -> Dict[int, bool]:
        session_ids = cls._session_ids_for_game(db_session, game_id)
        r_pipe = r.pipeline()
        for session_id in session_ids:
            r_pipe.hget(f"{RESTART_STATES_KEY}:{str(game_id)}", str(session_id))
        restart_states = r_pipe.execute()
        # This is sensitive to ordering... make sure pipelining preserves ordering
        result = {
            session_id: bool(restart_state)
            for restart_state, session_id in zip(restart_states, session_ids)
        }
        logger.debug("Restart states in game %s are:\n%s", game_id, result)
        return result

    @classmethod
    def connected_sessions_in_game(cls, db_session: 'DBSession', game_id: int) -> Set[int]:
        db_session_ids = cls._session_ids_for_game(db_session, game_id)
        connected_session_ids = r.smembers(
            f"{CONNECTED_SESSIONS_KEY}:{str(game_id)}"
        )
        result = db_session_ids.intersection({int(session_id) for session_id in connected_session_ids})
        logger.debug("Connected sessions in game %s are:\n%s", game_id, result)
        return result

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
            ready_states=self.ready_states,
            restart_states=self.restart_states,
            connected_sessions=self.connected_sessions,
        ).handle(
            message=message,
            session=session
        )
