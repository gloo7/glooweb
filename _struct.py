# -*- coding: utf-8 -*-
# @Author  : Gloo
# @time    : 2019/11/23 16:08
# @File    : ctx.py
# @Software: PyCharm


class Content(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"'Content' object has no attribute '{item}'")

    def __setattr__(self, key, value):
        self[key] = value


class NestedContent(Content):
    def __init__(self, global_content=None):
        super().__init__()
        self.global_content = global_content

    def relate(self, global_content):
        self.global_content = global_content

    def __getattr__(self, item):
        if item in self.keys():
            return self[item]
        return self.global_content[item]


class DictObject:
    def __init__(self, _dict):
        if isinstance(_dict, dict):
            self.__dict__['_dict'] = _dict
        else:
            self.__dict__['_dict'] = {}

    def __getattr__(self, item):
        try:
            return self._dict[item]
        except KeyError:
            return AttributeError(f"'DictObject' object has no attribute '{item}'")

    def __setattr__(self, key, value):
        raise NotImplementedError

    def items(self):
        return self._dict.items()
