import tornado.ioloop
import tornado.web
from server import GameStateHandler


def make_app():
    return tornado.web.Application([
        (r"/websocket", GameStateHandler)
    ])


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)  # TODO: ENV
    tornado.ioloop.IOLoop.current().start()
