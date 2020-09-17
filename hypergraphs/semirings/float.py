from hypergraphs.semirings import base
from collections import defaultdict

class Float:
    def __init__(self):
        assert False, 'should never be called'

    zero = 0.0
    one = 1.0

    @classmethod
    def lift(cls, x, _):
        return x

    @classmethod
    def chart(cls):
        return defaultdict(float)
