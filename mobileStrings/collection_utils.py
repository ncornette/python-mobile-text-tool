#!/usr/bin/env python
# coding=utf-8

# http://stackoverflow.com/a/18348004

import collections
from flask.json import JSONEncoder


def namedtuple_with_defaults(typename, field_names, default_values=()):
    T = collections.namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, collections.Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T


class StreamArrayJSONEncoder(JSONEncoder):
    def default(self, o):
        if hasattr(o, '__iter__'):
            return StreamArray(o)
        return JSONEncoder.default(self, o)

class StreamArray(list):

    def __init__(self, o):
        if not hasattr(o, '__iter__'):
            raise TypeError()
        self.generator = o

    def __iter__(self):
        return self.generator

    # http://stackoverflow.com/a/24033219
    # With Python 2.7.8, the StreamArray class also has to override the __len__ method
    # and returns a value greater than 0 (1 for instance). Otherwise the json encoder
    # doesn't even call the __iter__ method
    def __len__(self):
        return 1


if __name__ == '__main__':

    range_g = (v for v in range(10))
    assert json.dumps(range_g, cls=StreamArrayJSONEncoder) == '[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]'
    assert json.dumps(range_g, cls=StreamArrayJSONEncoder) == '[]'

    Foo = namedtuple_with_defaults("Foo", 'name', dict(name="bar"))

    assert Foo().name == "bar"
    assert Foo('blaz').name == "blaz"
    assert Foo(name='holy').name == "holy"

    Foo = namedtuple_with_defaults("Foo", 'name', dict(name="bar"))

    assert Foo().name == "bar"
    assert Foo('blaz').name == "blaz"
    assert Foo(name='holy').name == "holy"

    Foo = namedtuple_with_defaults("Foo", 'name grail', dict(name="bar"))

    assert Foo().name == "bar"
    assert Foo().grail is None
    assert Foo('blaz', True).grail == True
    assert Foo(name='holy').name == "holy"

    Foo = namedtuple_with_defaults("Foo", 'name grail', dict(name="bar"))

    assert Foo().name == "bar"
    assert Foo().grail is None
    assert Foo('blaz', True).grail == True
    assert Foo(name='holy').name == "holy"

