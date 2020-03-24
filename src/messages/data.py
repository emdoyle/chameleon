import attr
from typing import Dict, List


@attr.s(slots=True)
class OutgoingMessage:
    data = attr.ib(type=Dict)


@attr.s(slots=True)
class OutgoingMessages:
    messages = attr.ib(type=Dict[int, List[OutgoingMessage]], default=dict)
