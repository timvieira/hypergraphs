from hypergraphs.semirings import base

class MinTimes(base.Semiring):

    def __init__(self, score, d):
        self.score = score
        self.d = d

    def __add__(self, other):
        return min(self, other)

    def __mul__(self, other):
        if other is one: return self
        if self is one: return other
        if self is zero: return zero
        if other is zero: return zero
        return MinTimes(self.score * other.score, (self.d, other.d))

    def __lt__(self, other):
        return self.score < other.score

    def __repr__(self):
        return f'MinTimes({self.score}, {self.d})'


MinTimes.zero = zero = MinTimes(float('inf'), None)
MinTimes.one = one = MinTimes(1, ())
