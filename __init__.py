# -*- coding: utf-8 -*-
# @Author  : Gloo
# @time    : 2019/10/8 23:49
# @File    : http_response.py
# @Software: PyCharm
from .web import Gloo, Response
from .view import View
import json


def jsonify(**kwargs):
    content = json.dumps(kwargs)
    return Response(content, '200 ok', content_type="application/json", charset="utf-8")
