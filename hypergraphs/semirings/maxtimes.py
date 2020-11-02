from hypergraphs.semirings import base

class MaxTimes(base.Semiring):

    def __init__(self, score, d):
        self.score = score
        self.d = d

    def __add__(self, other):
        if other is zero: return self
        if self is zero: return other
        if self.score >= other.score:
            return self
        else:
            return other

    def __mul__(self, other):
        if other is one: return self
        if self is one: return other
        return MaxTimes(self.score * other.score, (self.d, other.d))

    def __lt__(self, other):
        return self.score < other.score

    def __repr__(self):
        return f'MaxTimes({self.score}, {self.d})'


MaxTimes.zero = zero = MaxTimes(0.0, None)
MaxTimes.one = one = MaxTimes(1.0, ())
