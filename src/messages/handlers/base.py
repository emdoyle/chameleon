import logging
from abc import ABC, abstractmethod
from typing import Dict, Set, Iterable, Optional, TYPE_CHECKING
from sqlalchemy.sql.expression import false
from src.services.game_state import GameStateService
from src.db import (
    Session, Game, Round, SetUpPhase, CluePhase, RevealPhase, User
)
from src.messages.builder import MessageBuilder
from src.settings import LOGGER_NAME
from ..data import OutgoingMessages

if TYPE_CHECKING:
    from src.db import (
        DBSession
    )

logger = logging.getLogger(LOGGER_NAME)


class AbstractMessageHandler(ABC):
    @classmethod
    @abstractmethod
    def factory(cls, *args, **kwargs):
        ...

    @abstractmethod
    def handle(self, message: Dict, session: 'Session') -> 'OutgoingMessages':
        ...


class BaseMessageHandler(AbstractMessageHandler):
    def __init__(
            self,
            db_session: 'DBSession',
            game_id: int
    ):
        self.db_session = db_session
        self.game_id = game_id
        self.message_builder = MessageBuilder.factory(
            db_session=db_session,
            game_id=game_id
        )

    @classmethod
    def factory(
            cls,
            db_session: 'DBSession',
            game_id: int
    ):
        return cls(
            db_session=db_session,
            game_id=game_id
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

    def _get_connected_sessions(self, game_id: int) -> Set[int]:
        game_state_service = GameStateService(db_session=self.db_session)
        return game_state_service.connected_sessions_in_game(game_id=game_id)

    def _get_connected_players(self, game_id: int) -> Iterable['User']:
        connected_sessions = self._get_connected_sessions(game_id=game_id)
        connected_session_ids = tuple(connected_sessions)
        return self.db_session.query(User).join(Session, Session.user_id == User.id).filter(
            Session.id.in_(connected_session_ids)
        ).all()

    def _get_chameleon_session_id(self, game_id: int) -> Optional[int]:
        set_up_phase = self._get_set_up_phase(game_id=game_id)
        if set_up_phase is None:
            logger.debug("Tried to get chameleon session id but none found with game id: %s", game_id)
            return None
        return set_up_phase.chameleon_session_id

    def _get_clue_turn_session_id(self, game_id: int, connected_sessions: Set[int]) -> Optional[int]:
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
            if str(session_id) not in clue_phase.clues and session_id in connected_sessions
        ), None)

    def _update_game_ending(self, game_id: int, winner: str) -> None:
        current_round = self._get_round(game_id)
        current_round.winner = winner
        self.db_session.add(current_round)
        self.db_session.commit()  # TODO: already in weird territory when it comes to committing unexpectedly

    def _default_messages(
            self, game_id: int, reset: bool = False
    ) -> 'OutgoingMessages':
        game_state_service = GameStateService(db_session=self.db_session)
        connected_sessions = game_state_service.connected_sessions_in_game(game_id=game_id)
        ready_states = game_state_service.ready_states_for_game(game_id=game_id)
        restart_states = game_state_service.restart_states_for_game(game_id=game_id)
        sessions_in_game = self._get_sessions_in_game(game_id)
        chameleon_session_id = self._get_chameleon_session_id(game_id)
        clue_turn_session_id = self._get_clue_turn_session_id(game_id, connected_sessions)
        full_game_state_message = self.message_builder.create_full_game_state_message(
            game_id=game_id,
            connected_sessions=connected_sessions,
            ready_states=ready_states,
            restart_states=restart_states
        )  # inefficient

        messages = {}
        for session_in_game in sessions_in_game:
            message_to_send = full_game_state_message
            if chameleon_session_id is not None and session_in_game.id == chameleon_session_id:
                logger.debug("Showing session %s that they are the chameleon!", session_in_game.id)
                message_to_send = full_game_state_message.add_chameleon()
            if clue_turn_session_id is not None and session_in_game.id == clue_turn_session_id:
                logger.debug("Showing session %s that it is their turn to give a clue!", session_in_game.id)
                message_to_send = message_to_send.add_is_clue_turn()
            if reset:
                logger.debug("Showing all sessions that this is a reset message")
                message_to_send = message_to_send.add_reset()
            messages[session_in_game.id] = [message_to_send]
        return OutgoingMessages(messages=messages)
