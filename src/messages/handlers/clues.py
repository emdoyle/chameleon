from typing import Dict, TYPE_CHECKING
from .base import BaseMessageHandler

if TYPE_CHECKING:
    from src.db import (
        Session
    )
    from ..data import OutgoingMessages


class ClueMessageHandler(BaseMessageHandler):
    def handle(self, message: Dict, session: 'Session') -> 'OutgoingMessages':
        if message['kind'] != 'clue':
            raise ValueError("ClueMessageHandler expects messages of kind 'clue'")

        # need to validate that this is coming from the right session
        # 1. retrieve session id which should currently be submitting a clue
        # 2. compare to this session id
        # 3. if match: update the DB with this clue and send default message
        # 4. if no match: log error and return no messages
        ...
