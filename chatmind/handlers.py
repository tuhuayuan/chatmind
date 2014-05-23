# -*- coding: UTF-8 -*-
import logging
import tornado.web
import tornado.gen
from utils import WechatSDKMixin


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self._dbsession = self.application.dbsession_maker()

    def on_finish(self):
        self._dbsession.close()

    @property
    def dbsession(self):
        return self._dbsession


class WechatHandler(BaseHandler, WechatSDKMixin):
    def prepare(self):
        self.wp_config(
            token=self.settings.get("wp_token"),
            appid=self.settings.get("wp_appid"),
            secret=self.settings.get("wp_secret")
        )

    @tornado.gen.coroutine
    def get(self):
        pass

    @tornado.gen.coroutine
    def post(self):
        pass


class YixinHandler(BaseHandler):
    pass
