import logging
from tornado.web import RequestHandler
from tornado.escape import json_encode, json_decode
from src.db import (
    DBSession,
    Session,
    User,
)
from src.settings import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class UserAPIHandler(RequestHandler):
    async def post(self):
        if self.get_secure_cookie(name="session_id"):
            logger.warning("User already has session, logging in as new user now")

        try:
            json_data = json_decode(self.request.body)
            username = json_data["username"]
        except (ValueError, KeyError):
            logger.error("Did not receive username.")
            self.send_error(status_code=400)
            return

        db_session = DBSession()
        new_user = User(username=username)
        logger.info(f"About to create user: {new_user}")
        db_session.add(new_user)
        db_session.commit()
        logger.info("Committed user!")

        new_session = Session(user_id=new_user.id,)
        logger.info(f"About to create session: {new_session}")
        db_session.add(new_session)
        db_session.commit()
        logger.info("Committed session!")

        self.set_secure_cookie(name="session_id", value=str(new_session.id))

        self.set_status(status_code=200)
        self.write(json_encode({"success": True}))
