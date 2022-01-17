import logging
from typing import Set, Dict
from sqlalchemy.sql.expression import false
from redis.exceptions import RedisError
from src.constants import CONNECTED_SESSIONS_KEY, READY_STATES_KEY, RESTART_STATES_KEY
from src.settings import LOGGER_NAME
from src.key_value import r
from src.db import (
    DBSession,
    Game,
    Round,
    Session,
    SetUpPhase,
    CluePhase,
    VotePhase,
    RevealPhase,
)

logger = logging.getLogger(LOGGER_NAME)


class GameStateService:
    def __init__(self, db_session: "DBSession"):
        self.db_session = db_session

    def create_game(self, game_name: str):
        new_game = Game(name=game_name)
        self.db_session.add(new_game)
        self.db_session.commit()
        logger.info("Committed game!")

        self.init_round(new_game.id)

    def init_round(self, game_id: int):
        new_round = Round(game_id=game_id,)
        self.db_session.add(new_round)
        self.db_session.commit()
        logger.info("Committed round!")

        self.db_session.add(SetUpPhase(round_id=new_round.id))
        self.db_session.add(CluePhase(round_id=new_round.id))
        self.db_session.add(VotePhase(round_id=new_round.id))
        self.db_session.add(RevealPhase(round_id=new_round.id))
        self.db_session.commit()
        logger.info("Committed phases!")

    def complete_current_round(self, game_id: int):
        current_round = (
            self.db_session.query(Round)
            .filter(Round.game_id == game_id)
            .filter(Round.completed == false())
            .first()
        )
        current_round.completed = True
        self.db_session.add(current_round)
        self.db_session.commit()

    def add_session_to_game(self, session_id: int, game_id: int):
        self.db_session.query(Session).filter(Session.id == session_id).update(
            {"game_id": game_id}
        )

    def disconnect_session(self, session_id: int, game_id: int):
        try:
            r.srem(f"{CONNECTED_SESSIONS_KEY}:{str(game_id)}", str(session_id))
        except RedisError:
            logger.warning(
                "Did not find connected sessions at key: %s",
                f"{CONNECTED_SESSIONS_KEY}:{str(game_id)}",
            )

        try:
            r.hdel(f"{READY_STATES_KEY}:{str(game_id)}", str(session_id))
        except RedisError:
            logger.warning(
                "Did not find session ready state for session %s at hash: %s",
                session_id,
                f"{READY_STATES_KEY}:{str(game_id)}",
            )

    def reset_game_state(self, game_id: int):
        try:
            r.delete(
                f"{READY_STATES_KEY}:{str(game_id)}",
                f"{RESTART_STATES_KEY}:{str(game_id)}",
            )
        except RedisError:
            logger.warning("Could not reset game state for game %s", str(game_id))

    def start_new_round(self, game_id: int):
        self.reset_game_state(game_id=game_id)
        self.complete_current_round(game_id=game_id)
        self.init_round(game_id=game_id)

    def session_ids_for_game(self, game_id: int) -> Set[int]:
        sessions_in_game = (
            self.db_session.query(Session)
            .join(Game, Game.id == Session.game_id)
            .filter(Game.id == game_id)
            .all()
        )
        return {session.id for session in sessions_in_game}

    def connected_sessions_in_game(self, game_id: int) -> Set[int]:
        db_session_ids = self.session_ids_for_game(game_id)
        connected_session_ids = r.smembers(f"{CONNECTED_SESSIONS_KEY}:{str(game_id)}")
        result = db_session_ids.intersection(
            {int(session_id) for session_id in connected_session_ids}
        )
        logger.debug("Connected sessions in game %s are:\n%s", game_id, result)
        return result

    def ready_states_for_game(self, game_id: int) -> Dict[int, bool]:
        session_ids = self.session_ids_for_game(game_id)
        # Should this also be async or is pipelining worth it?
        r_pipe = r.pipeline()
        for session_id in session_ids:
            r_pipe.hget(f"{READY_STATES_KEY}:{str(game_id)}", str(session_id))
        ready_states = r_pipe.execute()
        # This is sensitive to ordering... make sure pipelining preserves ordering
        result = {
            session_id: ready_state == "True"
            for ready_state, session_id in zip(ready_states, session_ids)
        }
        logger.debug("Ready states in game %s are:\n%s", game_id, result)
        return result

    # TODO: really think about whether it is useful to check Redis (since sessions clear on DC)
    def restart_states_for_game(self, game_id: int) -> Dict[int, bool]:
        session_ids = self.session_ids_for_game(game_id)
        # Should this also be async or is pipelining worth it?
        r_pipe = r.pipeline()
        for session_id in session_ids:
            r_pipe.hget(f"{RESTART_STATES_KEY}:{str(game_id)}", str(session_id))
        restart_states = r_pipe.execute()
        # This is sensitive to ordering... make sure pipelining preserves ordering
        result = {
            session_id: restart_state == "True"
            for restart_state, session_id in zip(restart_states, session_ids)
        }
        logger.debug("Restart states in game %s are:\n%s", game_id, result)
        return result

    def set_restart_state(self, session_id: int, game_id: int, restart_state: bool):
        r.hset(
            f"{RESTART_STATES_KEY}:{str(game_id)}", str(session_id), str(restart_state)
        )

    def set_ready_state(self, session_id: int, game_id: int, ready_state: bool):
        r.hset(f"{READY_STATES_KEY}:{str(game_id)}", str(session_id), str(ready_state))
