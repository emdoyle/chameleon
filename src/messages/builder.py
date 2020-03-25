from typing import Dict, List, Optional, TYPE_CHECKING
from sqlalchemy.sql.expression import false
from src.db import (
    DBSession,
    User,
    Round,
    Session,
    Game
)
from .data import OutgoingMessage

if TYPE_CHECKING:
    from src.db import (
        RevealPhase,
        VotePhase,
        CluePhase,
        SetUpPhase
    )


class MessageBuilder:
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
            ready_states: Dict[int, bool]
    ):
        return cls(db_session=db_session, ready_states=ready_states)

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
            'small_die_roll': set_up_phase.small_die_roll
        }

    @classmethod
    def _build_round_dict(cls, current_round: Optional['Round']) -> Dict:
        if current_round is None:
            return {}
        return {
            'round': {
                'id': current_round.id,
                'phase': current_round.phase,
                'completed': current_round.completed,
                'set_up': cls._build_set_up_dict(current_round.set_up_phase),
                'clue': cls._build_clue_dict(current_round.clue_phase),
                'vote': cls._build_vote_dict(current_round.vote_phase),
                'reveal': cls._build_reveal_dict(current_round.reveal_phase)
            }
        }

    def _build_players_dict(self, players: List['User']) -> Dict:
        return {
            'players': [
                {
                    'id': player.id,
                    'username': player.username,
                    'ready': self.ready_states[player.id]
                }
                for player in players
            ]
        }

    def create_full_game_state_message(
            self,
            session_id: int,
            game_id: int,
    ) -> 'OutgoingMessage':
        first_uncompleted_round = self.db_session.query(Round).filter(
            Round.game_id == game_id
        ).filter(Round.completed == false()).first()

        round_dict = self._build_round_dict(current_round=first_uncompleted_round)

        players_in_game = self.db_session.query(User).join(
            Session, Session.user_id == User.id
        ).join(
            Game, Session.game_id == Game.id
        ).filter(Session.id == session_id).all()
        players_dict = self._build_players_dict(players=players_in_game)

        return OutgoingMessage(
            data={**round_dict, **players_dict},
        )