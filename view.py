# -*- coding: utf-8 -*-
# @Author  : Gloo
# @time    : 2019/11/28 16:43
# @File    : view.py
# @Software: PyCharm
from .route import _Router
from functools import partial


class Mate(type):
    def __new__(cls, name, pts, attr):
        created = super().__new__(cls, name, pts, attr)
        route_name = attr.get("route_name", None)
        if not (route_name and isinstance(route_name, str)):
            route_name = name.lower()
        route_name = route_name if route_name.startswith('/') else '/'+route_name

        api = attr.get("api", None)

        if isinstance(api, _Router):
            for method in ('get', 'put', 'post', 'delete'):
                if method in attr:
                    api.route(route_name, method.upper())(partial(attr[method], created))

        return created


class View(metaclass=Mate):
    api = None
    route_name = None

    def get(self, *args, **kwargs):
        raise NotImplementedError("base view not implemented")

    def post(self, *args, **kwargs):
        raise NotImplementedError("base view not implemented")

    def put(self, *args, **kwargs):
        raise NotImplementedError("base view not implemented")

    def delete(self, *args, **kwargs):
        raise NotImplementedError("base view not implemented")
