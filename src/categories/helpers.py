import logging
from typing import Optional
from .root import CATEGORIES, KEYCARD

logger = logging.getLogger('chameleon')


def decode(category: str, big_die_roll: int, small_die_roll: int) -> Optional[str]:
    try:
        category_items = CATEGORIES[category]
    except KeyError:
        logger.error("Cannot find category for %s", category)
        return None
    decoded = KEYCARD[str(big_die_roll)][small_die_roll - 1]
    answer = category_items[decoded[0]][decoded[1] - 1].lower()
    logger.debug("Decoded big die: %s small die: %s to:\n%s", big_die_roll, small_die_roll, answer)
    return answer.lower()

