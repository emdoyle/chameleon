import tornado.ioloop
import tornado.web
from src.settings import BUILD_PATH, PORT, COOKIE_SECRET
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
from src.key_value import AIORedisContainer  # TODO: can pinject help here?


def make_app():
    return tornado.web.Application([
        (r"/websocket", GameStateHandler),
        (r"/api/v1/session", SessionAPIHandler),
        (r"/api/v1/user", UserAPIHandler),
        (r"/api/v1/games", GameAPIHandler),
        (CARD_PATHS, KeycardHandler, {'path': BUILD_PATH}),
        (r"/{}(.*)".format(BUILD_PATH), PublicAssetHandler, {'path': BUILD_PATH}),
        (r"/(.*)", RootHandler, {'path': BUILD_PATH}),
    ], cookie_secret=COOKIE_SECRET)


if __name__ == '__main__':
    app = make_app()
    app.listen(int(PORT))
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.run_sync(AIORedisContainer.set_client)
    io_loop.start()
