from hypergraphs.semirings import base

class MaxTimes(base.Semiring):

    def __init__(self, score, d):
        self.score = score
        self.d = d

    def __add__(self, other):
        return max(self, other)

    def __mul__(self, other):
        if other is one: return self
        if self is one: return other
        if self is zero: return zero
        if other is zero: return zero
        return MaxTimes(self.score * other.score, (self.d, other.d))

    def __lt__(self, other):
        return self.score < other.score

    def __repr__(self):
        return f'MaxTimes({self.score}, {self.d})'
#        return f'{self.score}'

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

MaxTimes.zero = zero = MaxTimes(float('-inf'), None)
MaxTimes.one = one = MaxTimes(1, ())
