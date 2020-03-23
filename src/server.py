import sys
import logging
from typing import Dict, List, Optional
from collections import defaultdict
from urllib.parse import urlparse
from tornado.web import StaticFileHandler, RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.escape import json_decode, json_encode
from sqlalchemy.sql.expression import false
from src.db import (
    DBSession, User, Session, Game, Round, SetUpPhase, CluePhase, VotePhase, RevealPhase
)
from src.settings import CORS_ORIGINS

logger = logging.getLogger('chameleon')  # TODO: ENV
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


class RootHandler(StaticFileHandler):
    def parse_url_path(self, url_path: str):
        return 'index.html'


class GameStateHandler(WebSocketHandler):
    waiters = set()
    ready_states = defaultdict(lambda: False)

    def check_origin(self, origin: str):
        parsed = urlparse(origin)
        return parsed.hostname in CORS_ORIGINS

    # TODO: repeated pattern
    @classmethod
    def _build_reveal_dict(cls, reveal_phase: Optional['RevealPhase']) -> Dict:
        if reveal_phase is None:
            return {}
        return {
            'guess': reveal_phase.guess
        }

    @classmethod
    def _build_vote_dict(cls, vote_phase: Optional['VotePhase']) -> Dict:
        if vote_phase is None:
            return {}
        return {
            'votes': vote_phase.votes
        }

    @classmethod
    def _build_clue_dict(cls, clue_phase: Optional['CluePhase']) -> Dict:
        if clue_phase is None:
            return {}
        return {
            'clues': clue_phase.clues
        }

    @classmethod
    def _build_set_up_dict(cls, set_up_phase: Optional['SetUpPhase']) -> Dict:
        if set_up_phase is None:
            return {}
        return {
            'category': set_up_phase.category,
            'big_die_roll': set_up_phase.big_die_roll,
            'small_die_roll': set_up_phase.small_die_roll
        }

    @classmethod
    def _build_round_dict(cls, current_round: Optional['Round']) -> Dict:
        if current_round is None:
            return {}
        return {
            'round': {
                'id': current_round.id,
                'phase': current_round.phase,
                'completed': current_round.completed,
                'set_up': cls._build_set_up_dict(current_round.set_up_phase),
                'clue': cls._build_clue_dict(current_round.clue_phase),
                'vote': cls._build_vote_dict(current_round.vote_phase),
                'reveal': cls._build_reveal_dict(current_round.reveal_phase)
            }
        }

    @classmethod
    def _build_players_dict(cls, players: List['User']) -> Dict:
        return {
            'players': [
                {
                    'id': player.id,
                    'username': player.username,
                    'ready': cls.ready_states[player.id]
                }
                for player in players
            ]
        }

    def send_initial_game_state(self, db_session: 'DBSession', session: 'Session'):
        first_uncompleted_round = db_session.query(Round).filter(
            Round.game_id == session.game_id
        ).filter(Round.completed == false()).first()

        round_dict = self._build_round_dict(current_round=first_uncompleted_round)

        players_in_game = db_session.query(User).join(
            Session, Session.user_id == User.id
        ).join(
            Game, Session.game_id == Game.id
        ).filter(Session.id == session.id).all()
        players_dict = self._build_players_dict(players=players_in_game)

        self.write_message({**round_dict, **players_dict})

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

    def open(self):
        logger.info("Opened websocket")
        db_session = DBSession()
        session = self.validate_session_from_cookie(db_session=db_session)
        if session is None:
            return

        self.player_id = session.user_id
        self.send_initial_game_state(db_session=db_session, session=session)
        GameStateHandler.waiters.add(self)

    @classmethod
    def send_updated_game_state(cls):
        ...

    def on_message(self, message):
        logger.info("Received message: {}".format(message))
        # TODO: take message and dispatch

    def on_close(self):
        logger.info("Closing websocket")
        GameStateHandler.waiters.remove(self)
        if hasattr(self, 'player_id') and self.player_id is not None:
            del GameStateHandler.ready_states[self.player_id]


class UserAPIHandler(RequestHandler):
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
            self.write(json_encode({'user_id': session.user_id, 'game_id': session.game_id}))
            return
        self.write(json_encode({'user_id': session.user_id}))

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
    async def post(self):
        session_id = self.get_secure_cookie(name="session_id")
        if not session_id:
            logger.error("Cannot create game without session.")
            self.send_error(status_code=400)
            return

        try:
            json_data = json_decode(self.request.body)
            game_name = json_data['gamename']
        except (ValueError, KeyError):
            logger.error("Did not receive game name.")
            self.send_error(status_code=400)
            return

        db_session = DBSession()
        new_game = Game(
            name=game_name
        )
        logger.info("About to create game")
        db_session.add(new_game)
        db_session.commit()
        logger.info("Committed game!")
        session = db_session.query(Session).filter_by(id=int(session_id)).first()
        session.game_id = new_game.id
        db_session.add(session)
        db_session.commit()
        logger.info(f"Added game_id: {new_game.id} to session with id: {session.id}")

        self.set_status(status_code=200)
        self.write(json_encode({'success': True}))
