from typing import Dict, TYPE_CHECKING
from .base import BaseMessageHandler

if TYPE_CHECKING:
    from src.db import (
        Session
    )
    from ..data import OutgoingMessages


class ReadyMessageHandler(BaseMessageHandler):
    @classmethod
    def handle(cls, message: Dict, session: 'Session') -> 'OutgoingMessages':
        ...
