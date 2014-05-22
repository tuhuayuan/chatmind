# -*- coding: UTF-8 -*-
import time
import json
import hashlib
import logging
import tornado.web
import tornado.gen
import xml.etree.ElementTree as ET
from app import BaseHandler
from datetime import datetime, timedelta
from tornado.concurrent import return_future
from tornado.options import define, options
from tornado.httpclient import AsyncHTTPClient
from StringIO import StringIO

define("mp_token", default="", help="")
define("mp_appid", default="", help="")
define("mp_appsecret", default="", help="")


class BaseHandler(tornado.web.RequestHandler):
    @property
    def dbsession(self):
        return None


class WechatHandler(BaseHandler, WechatMixin):
    def prepare(self):
        self.check_signature()

    @tornado.gen.coroutine
    def get(self):
        # for mp developer auth
        if "echostr" in self.request.query_arguments:
            self.set_header("Content-Type", "text/plain")
            self.write(self.get_argument("echostr"))
        else:
            pass

    @tornado.gen.coroutine
    def post(self):
        recv_msg = self.parse_msg()
        logging.debug(recv_msg)
        resp_msg = {
            "ToUserName": recv_msg["FromUserName"],
            "FromUserName": recv_msg["ToUserName"],
            "CreateTime": str(int(time.time())),
            "MsgType": "text",
            "Content": recv_msg["Content"]
        }
        self.set_header("Content-Type", "text/xml")
        self.write(self.build_msg(resp_msg))
