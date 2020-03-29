from typing import Dict, Optional, TYPE_CHECKING
from .base import BaseMessageHandler

if TYPE_CHECKING:
    from src.db import (
        Session
    )
    from ..data import OutgoingMessages


class VoteMessageHandler(BaseMessageHandler):
    @classmethod
    def _validate_vote(cls, vote: str) -> bool:
        ...

    def _update_game_state(self, session: 'Session', vote: Optional[str]) -> None:
        ...

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
            if self._validate_vote(vote):
                self._update_game_state(session, vote)
        elif action == 'clear':
            self._update_game_state(session, None)
        return self._default_messages(game_id=session.game_id, session_id=session.id, filter_self=False)
