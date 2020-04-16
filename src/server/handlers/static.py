import logging
from typing import Optional
from tornado.web import StaticFileHandler
from src.db import (
    DBSession,
    Game,
    Session,
    Round
)
from src.constants import CARD_FILE_NAMES, KEYCARD_FILE_NAME
from src.settings import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


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

        if path == KEYCARD_FILE_NAME:
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
