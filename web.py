# -*- coding: utf-8 -*-
# @Author  : Gloo
# @time    : 2019/10/7 19:11
# @File    : __init__.py
# @Software: PyCharm
from wsgiref.simple_server import make_server
from webob import Request, Response
from webob.dec import wsgify
from webob.exc import HTTPNotFound
from .route import _Router
from ._struct import Content
import logging


FORMAT = "%(levelname)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger('gloo')


class Gloo:
    Router = _Router
    Request = Request
    Response = Response

    _routes = {}
    ctx = Content()

    PRE_INTERCEPTOR = []
    POST_INTERCEPTOR = []

    def __init__(self, **kwargs):
        for k, v in kwargs:
            self.ctx.k = v
        self.ctx.app = self
        global current_app
        current_app = self

    @classmethod
    def register(cls, router: Router):
        cls._routes[router.prefix] = router
        router.ctx.relate(cls.ctx)
        return router

    @classmethod
    def reg_pre_interceptor(cls, fn):
        cls.PRE_INTERCEPTOR.append(fn)
        return fn

    @classmethod
    def reg_post_interceptor(cls, fn):
        cls.POST_INTERCEPTOR.append(fn)
        return fn

    @classmethod
    def extend(cls, name):
        if not callable(name):
            def _wrapper(ext):
                cls.ctx[name] = ext
                return ext
            return _wrapper
        return cls.extend(name.__name__)(name)

    @wsgify
    def __call__(self, request: Request, *args, **kwargs):
        for fn in self.PRE_INTERCEPTOR:
            request = fn(self.ctx, request)

        request_prefix = "/" + request.path.split("/")[1]
        if request_prefix in self._routes:
            response = self._routes[request_prefix].match(request)

            # 全局拦截响应
            for fn in self.POST_INTERCEPTOR:
                response = fn(request, response)
            if response:
                return response
        raise HTTPNotFound

    def runserver(self, ip="127.0.0.1", port=9999):
        server = make_server(ip, port, self)
        try:
            logger.info("WARNING: This is a development server. Do not use it in a production deployment.")
            logger.info(f"Running on http://{ip}:{port}/ (Press CTRL+C to quit)")
            server.serve_forever()
        except ConnectionResetError as e:
            logging.warning(e)
