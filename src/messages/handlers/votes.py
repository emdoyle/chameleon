import logging
from typing import Dict, Optional, TYPE_CHECKING
from collections import Counter
from src.settings import LOGGER_NAME
from .base import BaseMessageHandler

if TYPE_CHECKING:
    from src.db import (
        Session
    )
    from ..data import OutgoingMessages

logger = logging.getLogger(LOGGER_NAME)


class VoteMessageHandler(BaseMessageHandler):
    def _validate_vote(self, vote: str, game_id: int) -> bool:
        connected_players = self._get_connected_players(game_id)
        return vote in {
            player.username
            for player in connected_players
        }

    def _get_final_vote(self, votes: Dict[str, str], game_id: int) -> Optional[str]:
        counted_votes = Counter(votes.values())
        logger.debug("Counted votes: %s", counted_votes)
        if (
            {int(key) for key in votes.keys()} == self._get_connected_sessions(game_id=game_id)
            and len(counted_votes) <= 2
            and (len(counted_votes) == 1 or any(count <= 1 for count in counted_votes.values()))
        ):
            return counted_votes.most_common(1)[0][0]
        return None

    def _update_game_state(self, session: 'Session', vote: Optional[str]) -> None:
        current_round = self._get_round(session.game_id)
        vote_phase = current_round.vote_phase
        if vote is None:
            vote_phase.votes = {
                key: value
                for key, value
                in vote_phase.votes.items()
                if key != str(session.id)
            }
        else:
            vote_phase.votes = {**vote_phase.votes, str(session.id): vote}

        vote_phase.final_vote = self._get_final_vote(vote_phase.votes, session.game_id)
        self.db_session.add(vote_phase)
        if vote_phase.final_vote is not None:
            current_round.phase = 'reveal'
            self.db_session.add(current_round)
            # TODO: need caching or something, way too many queries throughout handlers
            chameleon_username = self._get_username_for_session_id(self._get_chameleon_session_id(session.game_id))
            if vote_phase.final_vote.lower() != chameleon_username.lower():
                self._update_game_ending(session.game_id, "The Chameleon")
        self.db_session.commit()

    def handle(self, message: Dict, session: 'Session') -> 'OutgoingMessages':
        if message['kind'] != 'vote':
            raise ValueError("VoteMessageHandler expects messages of kind 'vote")

        try:
            action = message['action']
        except KeyError:
            raise ValueError("Vote message must contain 'action' key")
        if action == 'set':
            try:
                vote = message['vote']
            except KeyError:
                raise ValueError("A 'set' action vote message requires a 'vote' key")
            if self._validate_vote(vote, session.game_id):
                self._update_game_state(session, vote)
        elif action == 'clear':
            self._update_game_state(session, None)
        return self._default_messages(game_id=session.game_id)
