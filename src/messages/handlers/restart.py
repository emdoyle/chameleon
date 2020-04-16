import logging
from typing import Dict, TYPE_CHECKING
from sqlalchemy.sql.expression import false
from src.db import (
    Game,
    Round,
    SetUpPhase,
    CluePhase,
    VotePhase,
    RevealPhase
)
from src.key_value import r  # TODO: should make all these handlers async... right?
from src.constants import RESTART_STATES_KEY
from src.settings import LOGGER_NAME
from .base import BaseMessageHandler
from ..data import OutgoingMessages

if TYPE_CHECKING:
    from src.db import (
        Session
    )

logger = logging.getLogger(LOGGER_NAME)


class RestartMessageHandler(BaseMessageHandler):
    def handle(self, message: Dict, session: 'Session') -> 'OutgoingMessages':
        if message['kind'] != 'restart':  # TODO: constants
            raise ValueError("RestartMessageHandler expects messages of kind 'restart'")

        try:
            restart_state = message['restart']
        except KeyError:
            raise ValueError("Malformed message sent to ReadyMessageHandler")

        self.restart_states[session.id] = restart_state
        r.hset(
            f"{RESTART_STATES_KEY}:{str(session.game_id)}",
            str(session.id),
            str(restart_state)
        )
        logger.debug('Restart states: %s', self.restart_states)
        filter_self = True  # TODO: this is some weird stuff

        if all((value for key, value in self.restart_states.items())):
            self._handle_full_restart(session.id, session.game_id)
            filter_self = False

        return self._default_messages(
            game_id=session.game_id,
            session_id=session.id,
            filter_self=filter_self,
        )

    def _handle_full_restart(self, session_id: int, game_id: int) -> None:
        game = self.db_session.query(Game, Game.id == game_id).first()
        current_round = self.db_session.query(Round, Round.game_id == game_id).filter(
            Round.completed == false()
        ).first()
        current_round.completed = False
        self.db_session.add(current_round)
        self.db_session.commit()

        round = Round(
            game_id=game.id,
        )
        self.db_session.add(round)
        self.db_session.commit()
        logger.info("Committed round!")

        self.db_session.add(SetUpPhase(round_id=round.id))
        self.db_session.add(CluePhase(round_id=round.id))
        self.db_session.add(VotePhase(round_id=round.id))
        self.db_session.add(RevealPhase(round_id=round.id))
        self.db_session.commit()
        logger.info("Committed phases!")

        session = self.db_session.query(Session).filter_by(id=session_id).first()
        session.game_id = game.id
        self.db_session.add(session)
        self.db_session.commit()
        logger.info(f"Added game_id: {game.id} to session with id: {session.id}")
