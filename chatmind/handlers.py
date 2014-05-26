# -*- coding: UTF-8 -*-
import time
import logging
import tornado.web
import tornado.gen
from utils import WechatSDKMixin
from models import User, Token, BaseModel


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
        WechatSDKMixin.mp_config(
            token=self.settings.get("mp_token"),
            appid=self.settings.get("mp_appid"),
            secret=self.settings.get("mp_secret")
        )

    @WechatSDKMixin.mp_check_signature
    @tornado.gen.coroutine
    def get(self):
        self.write(self.get_argument('echostr'))

    @WechatSDKMixin.mp_check_signature
    @tornado.gen.coroutine
    def post(self):
        ok, msg = self.mp_get_request()
        if ok:
            if msg.MsgType == 'event':
                if msg.Event == 'subscribe':
                    resp = self.mp_get_response(req=msg)
                    resp.Content = 'hello world'
                    self.mp_respond(resp)
            elif msg.MsgType == 'text':
                pass

    @tornado.gen.coroutine
    def get_access_token(self):
        token = Token.get_current_token(self.dbsession)
        if token.expired < int(time.time()):
            self.dbsession.delete(token)
            self.dbsession.flush()
            fetched = yield self.mp_get_token()
            token = Token(**fetched)
            self.dbsession.add(token)
            self.dbsession.commit()
        raise tornado.gen.Return(token.tokenid)


class YixinHandler(BaseHandler):
    pass
