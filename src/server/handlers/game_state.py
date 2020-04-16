import logging
from typing import Optional, Dict, Set
from urllib.parse import urlparse
from redis.exceptions import RedisError  # TODO: wrap these errors?
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler
from tornado.escape import json_decode, json_encode
from src.db import (
    DBSession,
    Game,
    Session,
)
from src.key_value import r, AIORedisContainer
from src.messages.data import OutgoingMessages
from src.messages.dispatch import MessageDispatch
from src.settings import CORS_ORIGINS, LOGGER_NAME
from src.constants import (
    GAME_TOPIC_KEY,
    READY_STATES_KEY,
    RESTART_STATES_KEY,
    CONNECTED_SESSIONS_KEY
)

logger = logging.getLogger(LOGGER_NAME)


class GameStateHandler(WebSocketHandler):
    waiters = {}

    @staticmethod
    def send_outgoing_messages(outgoing_messages: 'OutgoingMessages'):
        # This is how to publish to the game channel
        # r.publish(
        #     f"{GAME_TOPIC_KEY}:{str(game_id)}",
        #     "Some message indicating default state should be re-sent"
        # )
        for recipient, messages in outgoing_messages.messages.items():
            for outgoing_message in messages:
                json_data = json_encode(outgoing_message.data)
                logger.info("Writing message (%s)\nTo recipient %s", json_data, recipient)
                try:
                    GameStateHandler.waiters[recipient].write_message(json_encode(outgoing_message.data))
                except KeyError:
                    logger.warning("Recipient %s is not attached to websocket", recipient)

    @classmethod
    def _session_ids_for_game(cls, db_session: 'DBSession', game_id: int) -> Set[int]:
        sessions_in_game = db_session.query(Session).join(Game, Game.id == Session.game_id).filter(
            Game.id == game_id
        ).all()
        return {session.id for session in sessions_in_game}

    def ready_states_for_game(self, db_session: 'DBSession', game_id: int) -> Dict[int, bool]:
        session_ids = self._session_ids_for_game(db_session, game_id)
        r_pipe = r.pipeline()
        for session_id in session_ids:
            r_pipe.hget(f"{READY_STATES_KEY}:{str(game_id)}", str(session_id))
        ready_states = r_pipe.execute()
        # This is sensitive to ordering... make sure pipelining preserves ordering
        result = {
            session_id: bool(ready_state)
            for ready_state, session_id in zip(ready_states, session_ids)
        }
        logger.debug("Ready states in game %s are:\n%s", game_id, result)
        return result

    def connected_sessions_in_game(self, db_session: 'DBSession', game_id: int) -> Set[int]:
        db_session_ids = self._session_ids_for_game(db_session, game_id)
        connected_session_ids = r.smembers(
            f"{CONNECTED_SESSIONS_KEY}:{str(game_id)}"
        )
        result = db_session_ids.intersection({int(session_id) for session_id in connected_session_ids})
        logger.debug("Connected sessions in game %s are:\n%s", game_id, result)
        return result

    def check_origin(self, origin: str):
        parsed = urlparse(origin)
        return parsed.hostname in CORS_ORIGINS

    def validate_session_from_cookie(self, db_session: 'DBSession') -> Optional['Session']:
        session_id = self.get_secure_cookie(name="session_id")
        if session_id is None:
            logger.error("Cannot get game information without session.")
            self.close(code=400)
            return None

        current_session = db_session.query(Session).filter(Session.id == int(session_id)).first()

        if current_session is None:
            logger.error("Session no longer exists.")
            self.close(code=404)
            return None

        if current_session.game_id is None:
            logger.error("No game attached to this session.")
            self.close(code=404)
            return None
        return current_session

    async def _read_messages_from_channel(self, channel):
        while await channel.wait_message():
            msg = await channel.get()
            logger.info("Message: %s", msg)

    async def accept_from_redis_topic(self, game_id: int):
        aio_r = AIORedisContainer.get_client()
        subscription = await aio_r.subscribe(f"{GAME_TOPIC_KEY}:{str(game_id)}")
        logger.info("Subscribing to channel: %s", subscription[0])
        await self._read_messages_from_channel(subscription[0])

    def open(self):
        logger.info("Opened websocket")
        db_session = DBSession()
        session = self.validate_session_from_cookie(db_session=db_session)
        if session is None:
            return

        self.session_id = session.id
        GameStateHandler.waiters[self.session_id] = self
        # This adds to a Set in Redis
        r.sadd(
            f"{CONNECTED_SESSIONS_KEY}:{session.game_id}",
            str(session.id)
        )

        # This kicks off the redis subscription coroutine within the main IOLoop
        IOLoop.current().spawn_callback(
            lambda: self.accept_from_redis_topic(game_id=session.game_id),
        )

        db_session.close()

    def on_message(self, message):
        logger.info("Received message: {}".format(message))
        db_session = DBSession()
        session = self.validate_session_from_cookie(db_session=db_session)
        if session is None:
            return

        outgoing_messages = MessageDispatch.handle(
            message=json_decode(message),
            db_session=db_session,
            session=session,
            ready_states=self.ready_states_for_game(db_session, session.game_id),
            connected_sessions=self.connected_sessions_in_game(db_session, session.game_id),
        )
        GameStateHandler.send_outgoing_messages(outgoing_messages=outgoing_messages)
        db_session.close()

    def on_close(self):
        logger.info("Closing websocket")
        if (
            hasattr(self, 'session_id')
            and self.session_id is not None
        ):
            db_session = DBSession()
            current_session = db_session.query(Session).filter(Session.id == int(self.session_id)).first()
            if current_session is None:
                logger.warning("Closed websocket but did not find session %s in DB!")
                self.clear_session(self.session_id)
            else:
                self.clear_session(self.session_id, current_session.game_id)
            db_session.close()
        else:
            logger.warning("Closed websocket but did not remove self from memory!\nsession_id: %s", self.session_id)

    @classmethod
    def clear_session(cls, session_id: int, game_id: Optional[int] = None):
        try:
            del cls.waiters[session_id]
        except KeyError:
            logger.warning("Did not find active websocket connection for session %s", str(session_id))

        if game_id is None:
            return

        try:
            r.srem(
                f"{CONNECTED_SESSIONS_KEY}:{str(game_id)}",
                str(session_id)
            )
        except RedisError:
            logger.warning("Did not find connected sessions at key: %s", f"{CONNECTED_SESSIONS_KEY}:{str(game_id)}")

        try:
            r.hdel(
                f"{READY_STATES_KEY}:{str(game_id)}",
                str(session_id)
            )
        except RedisError:
            logger.warning(
                "Did not find session ready state for session %s at hash: %s",
                session_id,
                f"{READY_STATES_KEY}:{str(game_id)}"
            )
