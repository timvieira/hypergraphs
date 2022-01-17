from hypergraphs.semirings import base


class MaxPlus(base.Semiring):

    def __init__(self, score, d):
        self.score = score
        self.d = d

    def __add__(self, other):
        return max(self, other)

    def __mul__(self, other):
        if other is one: return self
        if self is one: return other
        if other is zero: return zero
        if self is zero: return zero
        return MaxPlus(self.score + other.score, [self.d, other.d])

    def __lt__(self, other):
        return self.score < other.score

    def __repr__(self):
        return f'MaxPlus({self.score}, {self.d})'

    @classmethod
    def multiplicity(cls,x,m):
        if m > 0:
            return x
        else:
            return cls.zero

    def __eq__(self, other):
        return self.score == other.score and self.d == other.d

    def __hash__(self):
        return hash((self.score, self.d))

    
MaxPlus.zero = zero = MaxPlus(float('-inf'), None)
MaxPlus.one = one = MaxPlus(0.0, ())
