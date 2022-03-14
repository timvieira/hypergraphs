from hypergraphs.semirings import base


class MaxPlus(base.Semiring):

    def __init__(self, score, d=None):
        self.score = score
        self.d = d

    def __repr__(self):
        return f'MaxPlus({self.score}, {self.d})'

    def __eq__(self, other):
        return isinstance(other, MaxPlus) and self.score == other.score

    def __hash__(self):
        return hash(self.score)

    @classmethod
    def samples(cls):
        return [
            cls(float('-inf')),
            #cls(float('+inf')),
            cls.zero,
            cls.one,
            cls(-3),
            cls(+3),
            cls(2),
            cls(-1)
        ]

    def __lt__(self, other):
        return isinstance(other, MaxPlus) and self.score < other.score

    def __add__(self, other):
        return max(self, other)

    def __mul__(self, other):
        if other is one: return self
        if self is one: return other
        if self is zero: return zero
        if other is zero: return zero
        return MaxPlus(self.score + other.score, [self.d, other.d])

    @classmethod
    def multiplicity(cls,x,m):
        if m > 0:
            return x
        else:
            return cls.zero

    def star(self):
        if self.score > 0: return MaxPlus(float('+inf'), None)
        return self.one + self


MaxPlus.zero = zero = MaxPlus(float('-inf'), None)
MaxPlus.one = one = MaxPlus(0.0, ())
