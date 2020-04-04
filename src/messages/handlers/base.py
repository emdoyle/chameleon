import logging
from abc import ABC, abstractmethod
from typing import Dict, Iterable, Optional, Type, TYPE_CHECKING
from sqlalchemy.sql.expression import false
from src.db import (
    Session, Game, Round, SetUpPhase, CluePhase, RevealPhase, User
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
            websocket_state: Type['GameStateHandler']
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
            connected_sessions: Dict[int, 'GameStateHandler'],
            websocket_state: Type['GameStateHandler']
    ):
        self.db_session = db_session
        self.ready_states = ready_states
        self.connected_sessions = connected_sessions
        self.websocket_state = websocket_state
        self.message_builder = MessageBuilder.factory(
            db_session=db_session,
            ready_states=ready_states,
            connected_sessions=connected_sessions,
            websocket_state=websocket_state
        )

    @classmethod
    def factory(
            cls,
            db_session: 'DBSession',
            ready_states: Dict[int, bool],
            connected_sessions: Dict[int, 'GameStateHandler'],
            websocket_state: Type['GameStateHandler']
    ):
        return cls(
            db_session=db_session,
            ready_states=ready_states,
            connected_sessions=connected_sessions,
            websocket_state=websocket_state
        )

    def _get_username_for_session_id(self, session_id: int) -> str:
        user = self.db_session.query(User).join(Session, Session.user_id == User.id).filter(
            Session.id == session_id
        ).first()
        if user is None:
            logger.error("Cannot get username for session %s", session_id)
        return user.username

    def _get_round(self, game_id: int) -> Optional['Round']:
        return self.db_session.query(Round).filter(
            Round.completed == false()
        ).filter(
            Round.game_id == game_id
        ).first()

    def _get_set_up_phase(self, game_id: int) -> Optional['SetUpPhase']:
        return self.db_session.query(SetUpPhase).join(
            Round, Round.id == SetUpPhase.round_id
        ).join(
            Game, Game.id == Round.game_id
        ).filter(
            Round.completed == false()
        ).filter(
            Game.id == game_id
        ).first()

    def _get_clue_phase(self, game_id: int) -> Optional['CluePhase']:
        return self.db_session.query(CluePhase).join(
            Round, Round.id == CluePhase.round_id
        ).join(
            Game, Game.id == Round.game_id
        ).filter(
            Round.completed == false()
        ).filter(
            Game.id == game_id
        ).first()

    def _get_reveal_phase(self, game_id: int) -> Optional['RevealPhase']:
        return self.db_session.query(RevealPhase).join(
            Round, Round.id == RevealPhase.round_id
        ).join(
            Game, Game.id == Round.game_id
        ).filter(
            Round.completed == false()
        ).filter(
            Game.id == game_id
        ).first()

    def _get_sessions_in_game(self, game_id: int) -> Iterable['Session']:
        return self.db_session.query(Session).filter(Session.game_id == game_id).all()

    def _get_connected_players(self) -> Iterable['User']:
        connected_session_ids = tuple(self.connected_sessions.keys())
        return self.db_session.query(User).join(Session, Session.user_id == User.id).filter(
            Session.id.in_(connected_session_ids)
        ).all()

    def _get_chameleon_session_id(self, game_id: int) -> Optional[int]:
        set_up_phase = self._get_set_up_phase(game_id=game_id)
        if set_up_phase is None:
            logger.debug("Tried to get chameleon session id but none found with game id: %s", game_id)
            return None
        return set_up_phase.chameleon_session_id

    def _get_clue_turn_session_id(self, game_id: int) -> Optional[int]:
        current_round = self._get_round(game_id=game_id)
        if current_round.phase != 'clue':
            logger.debug("Nobody's turn to give clues right now")
            return None
        set_up_phase = current_round.set_up_phase
        clue_phase = current_round.clue_phase
        if set_up_phase is None:
            logger.debug("Tried to get clue turn session id but none found with game id: %s", game_id)
            return None
        session_ordering = set_up_phase.session_ordering
        return next((
            session_id
            for session_id in session_ordering
            if str(session_id) not in clue_phase.clues and session_id in self.connected_sessions
        ), None)

    def _update_game_ending(self, game_id: int, winner: str) -> None:
        current_round = self._get_round(game_id)
        current_round.winner = winner
        self.db_session.add(current_round)
        self.db_session.commit()  # TODO: already in weird territory when it comes to committing unexpectedly

    def _default_messages(self, game_id: int, session_id: int, filter_self: bool = True) -> 'OutgoingMessages':
        sessions_in_game = self._get_sessions_in_game(game_id)
        chameleon_session_id = self._get_chameleon_session_id(game_id)
        clue_turn_session_id = self._get_clue_turn_session_id(game_id)
        full_game_state_message = self.message_builder.create_full_game_state_message(
            game_id=game_id
        )  # inefficient

        messages = {}
        for session_in_game in sessions_in_game:
            if filter_self and session_in_game.id == session_id:
                continue

            message_to_send = full_game_state_message
            if chameleon_session_id is not None and session_in_game.id == chameleon_session_id:
                logger.debug("Showing session %s that they are the chameleon!", session_in_game.id)
                message_to_send = full_game_state_message.add_chameleon()
            if clue_turn_session_id is not None and session_in_game.id == clue_turn_session_id:
                logger.debug("Showing session %s that it is their turn to give a clue!", session_in_game.id)
                message_to_send = message_to_send.add_is_clue_turn()
            messages[session_in_game.id] = [message_to_send]
        return OutgoingMessages(messages=messages)
