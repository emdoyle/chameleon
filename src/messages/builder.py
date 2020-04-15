import logging
from typing import Dict, Set, List, Optional, TYPE_CHECKING
from sqlalchemy import func
from sqlalchemy.sql.expression import false
from src.db import (
    DBSession,
    User,
    Round,
    Session
)
from src.categories import decode
from .data import OutgoingMessage

if TYPE_CHECKING:
    from src.db import (
        RevealPhase,
        VotePhase,
        CluePhase,
        SetUpPhase
    )

logger = logging.getLogger('chameleon')


class MessageBuilder:
    def __init__(
            self,
            db_session: 'DBSession',
            ready_states: Dict[int, bool],
            connected_sessions: Set[int]
    ):
        self.db_session = db_session
        self.ready_states = ready_states
        self.connected_sessions = connected_sessions

    @classmethod
    def factory(
            cls,
            db_session: 'DBSession',
            ready_states: Dict[int, bool],
            connected_sessions: Set[int]
    ):
        return cls(
            db_session=db_session,
            ready_states=ready_states,
            connected_sessions=connected_sessions,
        )

    @classmethod
    def _build_reveal_dict(cls, reveal_phase: Optional['RevealPhase']) -> Dict:
        if reveal_phase is None:
            return {}
        return {
            'guess': reveal_phase.guess
        }

    @classmethod
    def _build_vote_dict(cls, vote_phase: Optional['VotePhase']) -> Dict:
        if vote_phase is None:
            return {}
        return {
            'votes': vote_phase.votes
        }

    @classmethod
    def _build_clue_dict(cls, clue_phase: Optional['CluePhase']) -> Dict:
        if clue_phase is None:
            return {}
        return {
            'clues': clue_phase.clues
        }

    @classmethod
    def _build_set_up_dict(cls, set_up_phase: Optional['SetUpPhase']) -> Dict:
        if set_up_phase is None:
            return {}
        return {
            'category': set_up_phase.category,
            'big_die_roll': set_up_phase.big_die_roll,
            'small_die_roll': set_up_phase.small_die_roll,
        }

    @classmethod
    def _build_round_dict(cls, current_round: Optional['Round']) -> Dict:
        if current_round is None:
            return {}
        round_dict = {
            'round': {
                'id': current_round.id,
                'phase': current_round.phase,
                'completed': current_round.completed,
                'winner': current_round.winner,
                'set_up': cls._build_set_up_dict(current_round.set_up_phase),
                'clue': cls._build_clue_dict(current_round.clue_phase),
                'vote': cls._build_vote_dict(current_round.vote_phase),
                'reveal': cls._build_reveal_dict(current_round.reveal_phase),
            }
        }

        if current_round.winner:
            set_up_phase = current_round.set_up_phase
            round_dict['correct_answer'] = decode(
                set_up_phase.category,
                set_up_phase.big_die_roll,
                set_up_phase.small_die_roll
            )
        return round_dict

    def _build_players_dict(
            self,
            players: List['User'],
    ) -> Dict:
        result = {'players': []}
        for player in players:
            session_id = player.session.id
            if session_id not in self.connected_sessions:
                logger.error("Session %s has disconnected from the game!", player.id)
                continue
            entry = {
                'id': player.id,
                'session_id': session_id,
                'username': player.username,
                'ready': self.ready_states[session_id]
            }
            result['players'].append(entry)
        return result

    def create_full_game_state_message(
            self,
            game_id: int,
    ) -> 'OutgoingMessage':
        first_uncompleted_round = self.db_session.query(Round).filter(
            Round.game_id == game_id
        ).filter(Round.completed == false()).first()

        round_dict = self._build_round_dict(current_round=first_uncompleted_round)

        players_in_game = self.db_session.query(User).join(
            Session, Session.user_id == User.id
        ).filter(
            Session.game_id == game_id
        )

        if (
                first_uncompleted_round.set_up_phase is not None
                and first_uncompleted_round.set_up_phase.session_ordering is not None
        ):
            players_in_game = players_in_game.order_by(
                func.array_position(first_uncompleted_round.set_up_phase.session_ordering, Session.id)
            )

        players_dict = self._build_players_dict(
            players=players_in_game.all(),
        )

        return OutgoingMessage(
            data={**round_dict, **players_dict},
        )
