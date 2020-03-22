import tornado.ioloop
import tornado.web
from src.server import GameStateHandler, RootHandler


def make_app():
    return tornado.web.Application([
        (r"/websocket", GameStateHandler),
        (r"/(.*)", RootHandler, {'path': "assets/build/"}),  # TODO: ENV
    ])


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)  # TODO: ENV
    tornado.ioloop.IOLoop.current().start()
