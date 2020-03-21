import sys
import logging
from tornado.web import StaticFileHandler
from tornado.websocket import WebSocketHandler

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
