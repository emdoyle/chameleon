import tornado.ioloop
import tornado.web
from src.settings import COOKIE_SECRET
from src.server import (
    GameStateHandler,
    SessionAPIHandler,
    UserAPIHandler,
    GameAPIHandler,
    RootHandler,
    KeycardHandler
)


CARD_FILE_NAMES = [
    r"keycard.jpeg",
    r"chameleon_card.jpeg"
]
CARD_PATHS = r"/(" + r"|".join(CARD_FILE_NAMES) + r")"


def make_app():
    return tornado.web.Application([
        (r"/websocket", GameStateHandler),
        (r"/api/v1/session", SessionAPIHandler),
        (r"/api/v1/user", UserAPIHandler),
        (r"/api/v1/games", GameAPIHandler),
        (CARD_PATHS, KeycardHandler, {'path': "assets/build/"}),
        (r"/assets/build/(.*)", tornado.web.StaticFileHandler, {'path': "assets/build/"}),
        (r"/(.*)", RootHandler, {'path': "assets/build/"}),  # TODO: ENV
    ], cookie_secret=COOKIE_SECRET)


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)  # TODO: ENV
    tornado.ioloop.IOLoop.current().start()
