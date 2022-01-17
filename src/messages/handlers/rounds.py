from typing import Dict, TYPE_CHECKING
from .base import BaseMessageHandler
from ..data import OutgoingMessages

if TYPE_CHECKING:
    from src.db import Session


class RoundMessageHandler(BaseMessageHandler):
    def handle(self, message: Dict, session: "Session") -> "OutgoingMessages":
        if message["kind"] != "rounds":
            raise ValueError("RoundMessageHandler expects messages of kind 'rounds'")

        # here I basically want it to work the same way as the ready handler
        # except when it is finally ready, mark the previous game as completed,
        # create a new well-formed round under the same game id
        # and send a full state message to everyone

        return self._default_messages(game_id=session.game_id)
