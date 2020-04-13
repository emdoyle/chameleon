import tornado.ioloop
import tornado.web
from src.settings import COOKIE_SECRET
from src.server import (
    GameStateHandler,
    SessionAPIHandler,
    UserAPIHandler,
    GameAPIHandler,
    RootHandler,
    KeycardHandler,
    PublicAssetHandler,
)
from src.constants import (
    CARD_PATHS,
)
from src.key_value import AIORedisContainer


def make_app():
    return tornado.web.Application([
        (r"/websocket", GameStateHandler),
        (r"/api/v1/session", SessionAPIHandler),
        (r"/api/v1/user", UserAPIHandler),
        (r"/api/v1/games", GameAPIHandler),
        (CARD_PATHS, KeycardHandler, {'path': "assets/build/"}),
        (r"/assets/build/(.*)", PublicAssetHandler, {'path': "assets/build/"}),
        (r"/(.*)", RootHandler, {'path': "assets/build/"}),  # TODO: ENV
    ], cookie_secret=COOKIE_SECRET)


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)  # TODO: ENV
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.run_sync(AIORedisContainer.set_client)
    io_loop.start()
