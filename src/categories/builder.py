from typing import Dict, List
from collections import defaultdict

NUM_LETTERS = 4
LETTERS = [chr(ord("A") + i) for i in range(NUM_LETTERS)]
NUMBERS = [i for i in range(1, 5)]


def build_category(words: List[str]) -> Dict[str, List[str]]:
    result = defaultdict(list)
    index = 0
    for letter in LETTERS:
        for number in NUMBERS:
            result[letter].append(words[index])
            index += 1
    return result
