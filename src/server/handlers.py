import sys
import logging
from typing import Optional, Dict, Set
from collections import defaultdict
from functools import partial
from urllib.parse import urlparse
from tornado.web import StaticFileHandler, RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.ioloop import IOLoop
from tornado.escape import json_decode, json_encode
from src.db import (
    DBSession, User, Session, Game, Round,
    SetUpPhase, CluePhase, VotePhase, RevealPhase
)
from src.key_value import r, AIORedisContainer
from src.messages.data import OutgoingMessages
from src.messages.builder import MessageBuilder
from src.messages.dispatch import MessageDispatch
from src.settings import CORS_ORIGINS
from src.constants import (
    CARD_FILE_NAMES,
    GAME_TOPIC_KEY,
    READY_STATES_KEY,
    RESTART_STATES_KEY,
    CONNECTED_SESSIONS_KEY
)

logger = logging.getLogger('chameleon')  # TODO: ENV
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


class RootHandler(StaticFileHandler):
    def parse_url_path(self, url_path: str):
        return 'index.html'


class PublicAssetHandler(StaticFileHandler):
    async def get(self, path: str, include_body: bool = True):
        if path in CARD_FILE_NAMES:
            logger.error("Cannot serve protected file: %s from PublicAssetHandler", path)
            self.set_status(status_code=404)
            return
        return await super().get(path, include_body=include_body)


class KeycardHandler(StaticFileHandler):
    def validate_session_from_cookie(self, db_session: 'DBSession') -> Optional['Session']:
        session_id = self.get_secure_cookie(name="session_id")
        if session_id is None:
            logger.error("No session, no keycard.")
            return None
        current_session = db_session.query(Session).filter(Session.id == int(session_id)).first()

        if current_session is None:
            logger.error("Session no longer exists in DB.")
            return None

        if current_session.game_id is None:
            logger.error("No game attached to this session, no keycard.")
            return None
        return current_session

    async def get(self, path: str, include_body: bool = True):
        logger.debug('Getting card at path: %s', path)

        if path == 'keycard.jpeg':
            db_session = DBSession()
            validated_session = self.validate_session_from_cookie(db_session)
            if not validated_session:
                self.set_status(status_code=404)
                return
            current_round = db_session.query(Round).join(Game, Game.id == Round.game_id).filter(
                Game.id == validated_session.game_id
            ).first()
            if (
                current_round.phase == 'set_up'  # TODO: should _really_ be an ordered Enum
                or current_round.set_up_phase.chameleon_session_id == validated_session.id
            ):
                self.set_status(status_code=404)
                logger.error("Not the right player or time in the game for a keycard.")
                return

        return await super().get(path, include_body=include_body)


class GameStateHandler(WebSocketHandler):
    waiters = {}
    ready_states = defaultdict(lambda: False)

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
        # TODO: this is how to grab a bunch of ready states simultaneously from Redis
        # r_pipe = r.pipeline()
        # for session_id in session_ids:
        #     r_pipe.hget(READY_STATES_KEY, str(session_id))
        # ready_states = r_pipe.execute()
        # return {
        #     session_id: ready_state
        #     for ready_state, session_id in zip(ready_states, session_ids)
        # }
        return {
            session_id: self.ready_states[session_id]
            for session_id in session_ids
        }

    def connected_sessions_in_game(self, db_session: 'DBSession', game_id: int) -> Set[int]:
        db_session_ids = self._session_ids_for_game(db_session, game_id)
        connected_session_ids = r.get(
            f"{CONNECTED_SESSIONS_KEY}:{str(game_id)}"
        )
        return {
            session_id
            for session_id in connected_session_ids
            if session_id in db_session_ids
        }

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
        logger.debug("Ready states: %s", self.ready_states)
        logger.debug("Connected sesssions: %s", self.waiters)
        db_session = DBSession()
        session = self.validate_session_from_cookie(db_session=db_session)
        if session is None:
            return

        self.session_id = session.id
        GameStateHandler.waiters[self.session_id] = self
        # This is an 'append' operation to the given key
        r.lpush(
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
        logger.debug("Ready states: %s", self.ready_states)
        logger.debug("Connected sessions: %s", self.waiters)
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
            websocket_state=GameStateHandler
        )
        GameStateHandler.send_outgoing_messages(outgoing_messages=outgoing_messages)
        db_session.close()

    def on_close(self):
        logger.info("Closing websocket")
        if (
            hasattr(self, 'session_id')
            and self.session_id is not None
        ):
            self.clear_session(self.session_id)
        else:
            logger.warning("Closed websocket but did not remove self from memory!\nsession_id: %s", self.session_id)

    @classmethod
    def clear_session(cls, session_id: int):
        if session_id in GameStateHandler.waiters:
            del cls.waiters[session_id]
        if session_id in GameStateHandler.ready_states:
            del cls.ready_states[session_id]


class SessionAPIHandler(RequestHandler):
    async def get(self):
        session_id = self.get_secure_cookie(name="session_id")
        if not session_id:
            logger.info("No session found for this user.")
            self.set_status(status_code=200)
            return
        db_session = DBSession()
        session = db_session.query(Session).filter_by(id=int(session_id)).first()
        if not session:
            logger.info("No session found for this user.")
            self.set_status(status_code=200)
            return
        self.set_status(status_code=200)
        if session.game_id is not None:
            self.write(json_encode({'has_session': True, 'has_game': True}))
            return
        self.write(json_encode({'has_session': True}))
        db_session.close()

    async def delete(self):
        session_id = self.get_secure_cookie(name="session_id")
        db_session = DBSession()
        if session_id:
            GameStateHandler.clear_session(session_id=int(session_id))
            logger.debug("Cleared session %s from websocket handler", session_id)
            session = db_session.query(Session).filter(Session.id == int(session_id)).first()
            if session:
                db_session.delete(session)
                db_session.commit()
                logger.debug("Removed session %s from the DB", session_id)
            self.clear_cookie(name="session_id")
            logger.debug("Cleared cookie for session %s", session_id)
        else:
            logger.debug("No session id found")
        self.set_status(status_code=200)
        db_session.close()


class UserAPIHandler(RequestHandler):
    async def post(self):
        if self.get_secure_cookie(name="session_id"):
            logger.warning("User already has session, logging in as new user now")

        try:
            json_data = json_decode(self.request.body)
            username = json_data['username']
        except (ValueError, KeyError):
            logger.error("Did not receive username.")
            self.send_error(status_code=400)
            return

        db_session = DBSession()
        new_user = User(
            username=username
        )
        logger.info(f"About to create user: {new_user}")
        db_session.add(new_user)
        db_session.commit()
        logger.info("Committed user!")

        new_session = Session(
            user_id=new_user.id,
        )
        logger.info(f"About to create session: {new_session}")
        db_session.add(new_session)
        db_session.commit()
        logger.info("Committed session!")

        self.set_secure_cookie(
            name="session_id",
            value=str(new_session.id)
        )

        self.set_status(status_code=200)
        self.write(json_encode({'success': True}))


class GameAPIHandler(RequestHandler):
    async def get(self):
        session_id = self.get_secure_cookie(name="session_id")
        if not session_id:
            logger.error("Cannot create game without session.")
            self.send_error(status_code=400)
            return

        game_name = self.get_argument('gameName', None)
        db_session = DBSession()
        existing_game = db_session.query(Game).filter(Game.name == game_name).first()
        if existing_game is None:
            logger.error("Could not find game with name %s", game_name)
            self.send_error(status_code=404)
            return

        db_session.query(Session).filter(Session.id == int(session_id)).update({'game_id': existing_game.id})
        db_session.commit()
        db_session.close()
        return {'success': True}

    async def post(self):
        session_id = self.get_secure_cookie(name="session_id")
        if not session_id:
            logger.error("Cannot create game without session.")
            self.send_error(status_code=400)
            return

        try:
            json_data = json_decode(self.request.body)
            game_name = json_data['gameName']
        except (ValueError, KeyError):
            logger.error("Did not receive game name.")
            self.send_error(status_code=400)
            return

        db_session = DBSession()
        self._init_game(session_id=int(session_id), game_name=game_name, db_session=db_session)
        self.set_status(status_code=200)
        self.write(json_encode({'success': True}))
        db_session.close()

    def _init_game(
            self,
            session_id: int,
            game_name: str,
            db_session: 'DBSession'
    ):
        new_game = Game(
            name=game_name
        )
        db_session.add(new_game)
        db_session.commit()
        logger.info("Committed game!")

        new_round = Round(
            game_id=new_game.id,
        )
        db_session.add(new_round)
        db_session.commit()
        logger.info("Committed round!")

        db_session.add(SetUpPhase(round_id=new_round.id))
        db_session.add(CluePhase(round_id=new_round.id))
        db_session.add(VotePhase(round_id=new_round.id))
        db_session.add(RevealPhase(round_id=new_round.id))
        db_session.commit()
        logger.info("Committed phases!")

        session = db_session.query(Session).filter_by(id=session_id).first()
        session.game_id = new_game.id
        db_session.add(session)
        db_session.commit()
        logger.info(f"Added game_id: {new_game.id} to session with id: {session.id}")
