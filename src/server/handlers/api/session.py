import logging
from tornado.web import RequestHandler
from tornado.escape import json_encode
from src.db import DBSession, Session
from src.settings import LOGGER_NAME
from ..game_state import (
    GameStateHandler,
)  # TODO: this should be done with redis to avoid import

logger = logging.getLogger(LOGGER_NAME)


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
            self.write(json_encode({"has_session": True, "has_game": True}))
            return
        self.write(json_encode({"has_session": True}))
        db_session.close()

    async def delete(self):
        session_id = self.get_secure_cookie(name="session_id")
        db_session = DBSession()
        if session_id:
            session = (
                db_session.query(Session).filter(Session.id == int(session_id)).first()
            )
            if session:
                # TODO: this should probably be done through a redis channel as well
                GameStateHandler.clear_session(
                    session_id=int(session_id), game_id=int(session.game_id)
                )
                logger.debug("Cleared session %s from websocket handler", session_id)
                db_session.delete(session)
                db_session.commit()
                logger.debug("Removed session %s from the DB", session_id)
            self.clear_cookie(name="session_id")
            logger.debug("Cleared cookie for session %s", session_id)
        else:
            logger.debug("No session id found")
        self.set_status(status_code=200)
        db_session.close()
