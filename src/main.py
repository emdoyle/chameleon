import tornado.ioloop
import tornado.web
from src.settings import COOKIE_SECRET
from src.server import (
    GameStateHandler,
    SessionAPIHandler,
    UserAPIHandler,
    GameAPIHandler,
    RootHandler
)


def make_app():
    return tornado.web.Application([
        (r"/websocket", GameStateHandler),
        (r"/api/v1/session", SessionAPIHandler),
        (r"/api/v1/user", UserAPIHandler),
        (r"/api/v1/games", GameAPIHandler),
        (r"/assets/build/(.*)", tornado.web.StaticFileHandler, {'path': "assets/build/"}),
        (r"/(.*)", RootHandler, {'path': "assets/build/"}),  # TODO: ENV
    ], cookie_secret=COOKIE_SECRET)


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)  # TODO: ENV
    tornado.ioloop.IOLoop.current().start()
