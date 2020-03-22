import tornado.ioloop
import tornado.web
from src.settings import COOKIE_SECRET
from src.server import (
    GameStateHandler,
    UserAPIHandler,
    RootHandler
)


def make_app():
    return tornado.web.Application([
        (r"/websocket", GameStateHandler),
        (r"/api/v1/user", UserAPIHandler),
        (r"/(.*)", RootHandler, {'path': "assets/build/"}),  # TODO: ENV
    ], cookie_secret=COOKIE_SECRET)


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)  # TODO: ENV
    tornado.ioloop.IOLoop.current().start()
