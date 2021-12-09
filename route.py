# -*- coding: utf-8 -*-
# @Author  : Gloo
# @time    : 2019/11/23 20:58
# @File    : route.py
# @Software: PyCharm
from webob import Request
from ._struct import DictObject, NestedContent
import re


class _Router:
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

    def __init__(self, prefix: str = ""):
        self._prefix = prefix.rstrip("/\\")
        self._route_table = []

        self.pre_interceptor = []
        self.post_interceptor = []

        self.ctx = NestedContent()  # 未定义
        self.ctx.route = self

    def route(self, rule: str, *methods):
        def _wrapper(handler):
            pattern, translator = self.parse(rule)
            self._route_table.append((methods, re.compile(pattern), translator, handler))
            return handler
        wrapper = _wrapper
        return wrapper

    def get(self, pattern: str):
        return self.route(pattern, "GET")

    def head(self, pattern: str):
        return self.route(pattern, "HEAD")

    def post(self, pattern: str):
        return self.route(pattern, "POST")

    def put(self, pattern: str):
        return self.route(pattern, "PUT")

    def delete(self, pattern: str):
        return self.route(pattern, "DELETE")

    def match(self, request: Request):
        if not request.path.startswith(self._prefix):
            return

        # 依次执行拦截请求
        for fn in self.pre_interceptor:
            request = fn(self.ctx, request)

        tmp = request.path.replace(self._prefix, "", 1)
        relative_path = tmp if tmp.startswith("/") else "/" + tmp
        for methods, pattern, translator, handler in self._route_table:

            if not methods or request.method.upper() in methods:
                matcher = pattern.match(relative_path)
                if matcher:
                    newdict = {}
                    for k, v in matcher.groupdict().items():
                        newdict[k] = translator[k](v)
                    request.vars = DictObject(newdict)
                    response = handler(request)

                    # 依次执行拦截响应
                    for fn in self.post_interceptor:
                        response = fn(request, response)
                    return response

    @property
    def prefix(self):
        return self._prefix

    # 正则简化
    TYPE_PATTERNS = {
        "str": r"[^/]+",
        "word": r"\w+",
        "int": r"[+-]?\d+",
        "float": r"[+-]?\d+.\d+",
        "any": r".+"
    }
    TYPE_CASE = {
        "str": str,
        "word": str,
        "int": int,
        "float": float,
        "any": str
    }
    pattern = re.compile('{([^{}:]+):?([^{}:]*)}')

    @classmethod
    def transform(cls, kv: str):
        name, _, _type = kv.strip("{}").partition(":")
        return "(?P<{}>{})".format(name, cls.TYPE_PATTERNS.get(_type, r'\w+')), name, cls.TYPE_CASE.get(_type, str)

    @classmethod
    def parse(cls, src: str):
        start = 0
        res = ''
        translator = {}
        while True:
            matcher = cls.pattern.search(src, start)
            if matcher:
                res += matcher.string[start: matcher.start()]
                tmp = cls.transform(matcher.group())
                res += tmp[0]
                translator[tmp[1]] = tmp[2]
                start = matcher.end()
            else:
                res += src[start:]+'$'
                break

        return res, translator

    def reg_pre_interceptor(self, fn):
        self.pre_interceptor.append(fn)
        return fn

    def reg_post_interceptor(self, fn):
        self.post_interceptor.append(fn)
        return fn


