import sys
import logging
from tornado.web import StaticFileHandler, RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.escape import json_decode, json_encode
from src.db import DBSession, User

logger = logging.getLogger('chameleon')  # TODO: ENV
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


class RootHandler(StaticFileHandler):
    def parse_url_path(self, url_path: str):
        if not url_path or url_path.endswith('/'):
            url_path = url_path + 'index.html'
        return url_path


class GameStateHandler(WebSocketHandler):
    def open(self):
        logger.info("open")

    def on_message(self, message):
        logger.info("on_message:{}".format(message))

    def on_close(self):
        logger.info("on_close")


class UserAPIHandler(RequestHandler):
    def initialize(self):
        ...

    def get(self):
        ...

    def post(self):
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
        logger.info("Committed!")
        self.set_status(status_code=200)
        self.write(json_encode({'success': True}))
