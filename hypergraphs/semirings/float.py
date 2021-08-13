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

    @staticmethod
    def star(x):
        return 1/(1-x)

    @classmethod
    def multiplicity(cls,x,m):
        return x*m
