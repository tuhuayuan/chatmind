# -*- coding: UTF-8 -*-
import tornado.web
import tornado.httpserver
import tornado.ioloop
import wechat
from tornado.options import define, options


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/wechat_index", wechat.IndexHandler)
        ]
        settings = {
            'debug': options.debug
        }
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def dbsession(self):
        return None


def main():
    define("port", default=2080, help="run on the givent port", type=int)
    define("debug", default=False, help="run in debug mode", type=bool)
    define("config", default="", help="load the givent config file")
    tornado.options.parse_command_line()
    try:
        tornado.options.parse_config_file(options.config)
    except IOError:
        options.print_help()
        return
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
