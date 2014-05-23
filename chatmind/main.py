# -*- coding: UTF-8 -*-
import os
import tornado.web
import tornado.httpserver
import tornado.ioloop
import models
from tornado.options import define, options, parse_config_file
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from handlers import WechatHandler, YixinHandler

define("port", default=2080, help="run on the givent port", type=int)
define("debug", default=False, help="run in debug mode", type=bool)
define(
    "config",
    default="",
    help="load the givent config file",
    callback=lambda path: parse_config_file(path, final=False)
)
define("db_connect_string", default="sqlite://:memory", help="load the givent config file")
define("db_rebuild", default=False, help="drop all database table", type=bool)
define("mp_token", default="", help="token for your mp account")
define("mp_appid", default="", help="mp account appid")
define("mp_secret", default="", help="mp account app secret")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/wechat_index", WechatHandler),
            (r"/yinxin_index", YixinHandler),
        ]
        settings = dict(
            # server settings
            debug=options.debug,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            static_url="/public/",
            xsrf_cookies=True,
            cookie_secret="wxb0b2ff9c2e34505d",
            # wechat sdk settings
            wp_token=options.wp_token,
            wp_appid=options.wp_appid,
            wp_secret=options.wp_secret
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.engine = create_engine(options.db_connect_string, echo=options.debug)
        self.dbsession_maker = sessionmaker(bind=self.engine)
        if options.db_rebuild:
            models.drop_db(self.engine)
        models.init_db(self.engine)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
