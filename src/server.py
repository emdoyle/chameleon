import sys
import logging
from tornado.websocket import WebSocketHandler

logger = logging.getLogger('chameleon')  # TODO: ENV
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


class GameStateHandler(WebSocketHandler):
    def open(self):
        logger.info("open")

    def on_message(self, message):
        logger.info("on_message:{}".format(message))

    def on_close(self):
        logger.info("on_close")
