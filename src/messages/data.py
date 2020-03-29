import attr
import logging
from typing import Dict, List
from copy import deepcopy

logger = logging.getLogger('chameleon')


@attr.s(slots=True)
class OutgoingMessage:
    data = attr.ib(type=Dict)

    def augment(self, chameleon_session_id: int) -> 'OutgoingMessage':
        logger.debug("Showing session %s that they are the chameleon!", chameleon_session_id)
        data = deepcopy(self.data)
        try:
            player = next((player for player in data['players'] if player['session_id'] == chameleon_session_id), None)
        except KeyError:
            logger.error("Tried to augment incomplete outgoing message for chameleon id: %s", chameleon_session_id)
            return OutgoingMessage(data=data)
        if player is None:
            logger.error("Tried to augment chameleon id %s but couldn't find corresponding player", chameleon_session_id)
            return OutgoingMessage(data=data)
        player['chameleon'] = True
        return OutgoingMessage(data=data)


@attr.s(slots=True)
class OutgoingMessages:
    messages = attr.ib(type=Dict[int, List[OutgoingMessage]], default=dict)

    def merge(self, other: 'OutgoingMessages') -> 'OutgoingMessages':
        merged_messages = {**self.messages}
        for key, value in other.messages:
            if key in merged_messages:
                merged_messages[key].extend(value)
            else:
                merged_messages[key] = value
        return OutgoingMessages(
            messages=merged_messages
        )
