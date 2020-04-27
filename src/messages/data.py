import attr
from typing import Dict, List
from copy import deepcopy
from json import loads, dumps


@attr.s(slots=True)
class OutgoingMessage:
    data = attr.ib(type=Dict)

    # TODO: reconsider this immutable-style stuff

    def add_chameleon(self) -> 'OutgoingMessage':
        data = deepcopy(self.data)
        data['chameleon'] = True
        return OutgoingMessage(data=data)

    def add_is_clue_turn(self) -> 'OutgoingMessage':
        data = deepcopy(self.data)
        data['is_clue_turn'] = True
        return OutgoingMessage(data=data)

    def add_reset(self) -> 'OutgoingMessage':
        data = deepcopy(self.data)
        data['reset'] = True
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

    # TODO: could really go crazy with abstractions here... not necessary now
    def serialize_as_json(self) -> str:
        return dumps(attr.asdict(self))

    @classmethod
    def deserialize_from_json(cls, serialized_messages: str) -> 'OutgoingMessages':
        return cls(**loads(serialized_messages))
