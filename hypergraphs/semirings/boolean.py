from hypergraphs.semirings import base


class Boolean(base.Semiring):

    def __init__(self, score, d):
        self.score = (score > 0)
        self.d = d

    def __add__(self, other):
        return max(self, other)

    def __mul__(self, other):
        if other is one: return self
        if self is one: return other
        if other is zero: return zero
        if self is zero: return zero
        return Boolean(self.score and other.score, [self.d, other.d])

    def __eq__(self, other):
        return self.score == other.score and self.d == other.d

    def __lt__(self, other):
        return self.score < other.score

    def __repr__(self):
        return f'Boolean({self.score}, {self.d})'

    @classmethod
    def lift(cls, score, d):
        if isinstance(score, Boolean):
            return score
        else:
            return cls(score, d)

    @classmethod
    def multiplicity(cls,x,m):
        if m > 0:
            return x
        else:
            return cls.zero


Boolean.zero = zero = Boolean(False, None)
Boolean.one = one = Boolean(True, ())
