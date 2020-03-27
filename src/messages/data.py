import attr
from typing import Dict, List


@attr.s(slots=True)
class OutgoingMessage:
    data = attr.ib(type=Dict)


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
