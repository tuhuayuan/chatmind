# -*- coding: UTF-8 -*-
import time
import json
import hashlib
import logging
import tornado.web
import tornado.gen
import xml.etree.ElementTree as ET
from functools import wraps
from datetime import datetime, timedelta
from tornado.httpclient import AsyncHTTPClient
from tornado.util import ObjectDict
from StringIO import StringIO
from models import Token


class WechatSDKMixin(object):
    __appurl__ = "https://api.weixin.qq.com/cgi-bin/"
    __tpl__ = dict(
        base={'ToUserName': '', 'FromUserName': '', 'CreateTime': 0, 'MsgType': ''},
    )

    def mp_config(self, token="", appid="", secret=""):
        self.__apptoken__ = token
        self.__appid__ = appid
        self.__appsecret__ = secret

    def mp_check_signature(method):
        """Decorate methods with this to check the request signature
        signature = sha1(sort([token, timestamp, nonce]))
        """
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            signature = self.get_argument("signature")
            l = sorted([self.__apptoken__,
                self.get_argument("timestamp"),
                self.get_argument("nonce")])
            if hashlib.sha1("".join(l)).hexdigest() == signature:
                return method(self, *args, **kwargs)
            else:
                raise tornado.web.HTTPError(403)
        return wrapper

    @tornado.gen.coroutine
    def mp_get_token(self, cb=None):
        """Coroutine methods, yield this to check api access token,
        if exprired than fetch new token from server
        @cb: use callback to get result
        TODO: Save global token to memorydb(redis or memcached)
        """
        tk = self.dbsession.query(Token).with_for_update().first()
        if tk.expired < datetime.now():
            http_client = AsyncHTTPClient()
            resp = yield http_client.fetch(self.mp_api_url +
                    "token?grant_type=client_credential" +
                    "&appid={0}&secret={1}".format(self.__appid__, self.__appsecret__))
            if resp.code == 200:
                msg = json.load(StringIO(resp.body))
                tk.token = msg['access_token']
                tk.expired = timedelta(msg['expires_in']) + datetime.now()
                self.dbsession.commit()
            else:
                logging.warning("mp_access_token error code: %n", resp.code)
        if cb is not None:
            cb(tk.token)
        else:
            raise tornado.gen.Return(tk.token)

    def mp_get_request(self):
        """ Parse MP request msg from http request body in xml format
        return: bool, an instance of ObjectDict
        """
        ok = True
        msg = ObjectDict()
        try:
            root = ET.fromstring(self.request.body)
            for elem in root:
                msg[elem.tag] = elem.text
        except ET.ParseError:
            ok = False
            logging.warning("mp request body not well formed")
        return ok, msg

    def mp_get_response(self, req=None, resp_type="text"):
        """ Create a ObjectDict instance with given response type\
        if type not support return plaint text type object
        @req: build the instance for given request
        @resp_type: response message type
        return: an instance of ObjectDict
        """
        base = WechatSDKMixin.__tpl__['base']
        tpl = WechatSDKMixin.__tpl__.get(resp_type)
        if tpl is None:
            base.update(tpl)
        if req is not None:
            base.FromUserName, base.ToUserName = req.ToUserName, req.FromUserName
        base.CreateTime = int(time.timestamp())

    @tornado.gen.coroutine
    def mp_send(self, msg, cb=None):
        """Coroutine method,first convert msg from ObjectDict to json string,
        than send to mp server
        @cb: use callback to get result
        return: mp global error code
        """
        pass

    def mp_respond(self, msg):
        """Convert msg from ObjectDict to Xml string, than write into http
        response
        """
        pass
