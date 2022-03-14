from hypergraphs.semirings import base
from collections import defaultdict

class Float(base.Semiring):
    def __init__(self):
        assert False, 'should never be called'

    zero = 0.0
    one = 1.0

    @classmethod
    def samples(clse):
        return [
            #float('-inf'),
            #float('+inf'),
            0, -3, 2, #2.18,
            1, -1,
        ]

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

    @classmethod
    def multiple(cls,m):
        return m

    def star_approx(self, T):
        v = 1
        for _ in range(T):
            v += self * v
        return v
