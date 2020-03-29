import attr
import logging
from typing import Dict, List
from copy import deepcopy

logger = logging.getLogger('chameleon')


@attr.s(slots=True)
class OutgoingMessage:
    data = attr.ib(type=Dict)

    def add_chameleon(self) -> 'OutgoingMessage':
        data = deepcopy(self.data)
        data['chameleon'] = True
        return OutgoingMessage(data=data)

    def add_is_clue_turn(self) -> 'OutgoingMessage':
        data = deepcopy(self.data)
        data['is_clue_turn'] = True
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
