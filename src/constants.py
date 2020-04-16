KEYCARD_FILE_NAME = "keycard.jpeg"
CARD_FILE_NAMES = [
    r"small_die.svg",
    r"keycard.jpeg",
    r"chameleon_card.jpeg",
    r"arts.jpeg",
    r"games.jpeg",
    r"hobbies.jpeg",
    r"movies.jpeg",
    r"music.jpeg",
    r"transport.jpeg"
    # TODO: other categories
]
CARD_PATHS = r"/(" + r"|".join(CARD_FILE_NAMES) + r")"

GAME_TOPIC_KEY = "$CHAMELEONGAME$"
CONNECTED_SESSIONS_KEY = "$CONNECTEDSESSIONS$"
READY_STATES_KEY = "$READYSTATES$"
RESTART_STATES_KEY = "$RESTARTSTATES$"
