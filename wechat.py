import json
import hashlib
import logging
import tornado.web
import tornado.gen
from app import BaseHandler
from datetime import datetime, timedelta
from tornado.concurrent import return_future
from tornado.options import define, options
from tornado.httpclient import AsyncHTTPClient
from StringIO import StringIO

define("mp_token", default="", help="")
define("mp_appid", default="", help="")
define("mp_appsecret", default="", help="")


class WechatMixin(object):
    _access_token = ""
    _access_token_expired = datetime.today()
    _access_path = "https://api.weixin.qq.com/cgi-bin/"

    def check_signature(self):
        signature = self.get_argument("signature")
        lst = [
            options.mp_token,
            self.get_argument("timestamp"),
            self.get_argument("nonce")
        ]
        lst.sort()
        if hashlib.sha1("".join(lst)).hexdigest() == signature:
            return True
        else:
            raise tornado.web.HTTPError(404)

    @return_future
    def get_access_token(self, callback):
        future = callback
        if WechatMixin._access_token == "" or \
                WechatMixin._access_token_expired < datetime.now():
            http_client = AsyncHTTPClient()
            cmd = WechatMixin._access_path + \
                "token?grant_type=client_credential" + \
                self._access_param
            http_client.fetch(cmd, self.async_callback(
                self._future_get_access_token, future
                )
            )
        else:
            future(WechatMixin._access_token)

    def _future_get_access_token(self, future, response):
        if response.code == 200:
            body = json.load(StringIO(response.body))
            WechatMixin._access_token = body['access_token']
            WechatMixin._access_token_expired = timedelta(body['expires_in']) + datetime.now()
            logging.debug("mp_access_token:  %s", WechatMixin._access_token)
            future(WechatMixin._access_token)
        else:
            logging.warning("Fetch mp_access_token Error %n", response.code)

    @property
    def _access_param(self):
        return "&appid={0}&secret={1}".format(
            options.mp_appid,
            options.mp_appsecret
        )


class IndexHandler(BaseHandler, WechatMixin):
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
        print(yield self.get_access_token())
