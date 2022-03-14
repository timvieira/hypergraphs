import numpy as np
from hypergraphs.semirings import base


class Boolean(base.Semiring):

    def __init__(self, score, d=None):
        self.score = (score > 0)
        self.d = d

    @classmethod
    def samples(cls):
        return [cls(True), cls(False)]

    def __add__(self, other):
        return max(self, other)

    def __mul__(self, other):
        if other is one: return self
        if self is one: return other
        if other is zero: return zero
        if self is zero: return zero
        return Boolean(self.score and other.score, [self.d, other.d])

    def __hash__(self):
        return hash(self.score)

    def __eq__(self, other):
        return self.score == other.score

    def __lt__(self, other):
        return self.score < other.score

    def __repr__(self):
#        return f'Boolean({self.score}, {self.d})'
        return f'{self.score}'

    def star(self):
        return one

    @classmethod
    def lift(cls, score, d):
        if isinstance(score, Boolean):
            return score
        else:
            return cls(score, d)

    @classmethod
    def multiplicity(cls,v,m):
        if m > 0:
            return v
        else:
            return cls.zero


Boolean.zero = zero = Boolean(False, None)
Boolean.one = one = Boolean(True, ())
