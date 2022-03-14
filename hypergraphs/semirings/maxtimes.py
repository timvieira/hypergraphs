from hypergraphs.semirings import base


class MaxTimes(base.Semiring):

    def __init__(self, score, d=None):
        self.score = score
        self.d = d

    def __repr__(self):
        return f'MaxTimes({self.score}, {self.d})'

    def __eq__(self, other):
        return isinstance(other, MaxTimes) and self.score == other.score

    def __hash__(self):
        return hash(self.score)

    @classmethod
    def samples(cls):
        return [
            cls.zero,
            cls.one,
            cls(3),
            cls(2),
            #cls(2.18),
        ]

    def __lt__(self, other):
        return isinstance(other, MaxTimes) and self.score < other.score

    def __add__(self, other):
        return max(self, other)

    def __mul__(self, other):
        if other is one: return self
        if self is one: return other
        if self is zero: return zero
        if other is zero: return zero
        return MaxTimes(self.score * other.score, (self.d, other.d))

    @classmethod
    def multiplicity(cls,x,m):
        if m > 0:
            return x
        else:
            return cls.zero

    def star(self):
        if self.score > 0: return MaxTimes(float('+inf'), None)
        return self.one + self


MaxTimes.zero = zero = MaxTimes(0, None)
MaxTimes.one = one = MaxTimes(1, ())
