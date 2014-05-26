# -*- coding: UTF-8 -*-
import time
import json
import hashlib
import logging
import tornado.web
import tornado.gen
import xml.etree.ElementTree as ET
from functools import wraps
from tornado.httpclient import AsyncHTTPClient
from tornado.util import ObjectDict
from StringIO import StringIO


class WechatSDKMixin(object):
    __appurl__ = "https://api.weixin.qq.com/cgi-bin/"
    __tpl__ = dict(
        base=ObjectDict(ToUserName='', FromUserName='', CreateTime='', MsgType=''),
        text=ObjectDict(Content='text'),
    )

    @classmethod
    def mp_config(cls, token="", appid="", secret=""):
        cls.__apptoken__ = token
        cls.__appid__ = appid
        cls.__appsecret__ = secret

    @staticmethod
    def mp_check_signature(method):
        """Decorate methods with this to check the request signature
        signature = sha1(sort([token, timestamp, nonce]))
        """
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            signature = self.get_argument("signature")
            l = sorted([WechatSDKMixin.__apptoken__,
                self.get_argument("timestamp"),
                self.get_argument("nonce")])
            if hashlib.sha1("".join(l)).hexdigest() == signature:
                return method(self, *args, **kwargs)
            else:
                raise tornado.web.HTTPError(403)
        return wrapper

    @tornado.gen.coroutine
    def mp_get_token(self):
        """Coroutine methods, yield this to check api access token,
        @cb: use callback to get result
        TODO: Save global token to memorydb(redis or memcached)
        @return ObjectDict(tokenid, expired)
        """
        tk = ObjectDict(tokenid='', expired=0)
        http_client = AsyncHTTPClient()
        resp = yield http_client.fetch(WechatSDKMixin.__appurl__ +
                "token?grant_type=client_credential" +
                "&appid={0}&secret={1}".format(
                    WechatSDKMixin.__appid__,
                    WechatSDKMixin.__appsecret__))
        if resp.code == 200:
            msg = json.load(StringIO(resp.body))
            tk.tokenid = msg['access_token']
            tk.expired = int(time.time() + msg['expires_in'])
        else:
            logging.warning("mp_access_token error code: %n", resp.code)
        raise tornado.gen.Return(tk)

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
        if tpl is not None:
            base.update(tpl)
        if req is not None:
            base.FromUserName, base.ToUserName = req.ToUserName, req.FromUserName
        base.CreateTime = str(int(time.time()))
        base.MsgType = resp_type
        return base

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
        r = ET.Element('xml')

        def _build_node(parent, d):
            for k, v in msg.items():
                if isinstance(v, dict):
                    _build_node(child, v)
                elif isinstance(v, list):
                    [_build_node(vv) for vv in v if isinstance(vv, dict)]
                else:
                    child = ET.SubElement(parent, k)
                    child.text = v
                    print(ET.tostring(child))
        _build_node(r, msg)
        self.set_header("Content-Type", "text/xml")
        self.write(ET.tostring(r))
