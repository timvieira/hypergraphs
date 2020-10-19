from hypergraphs.semirings import base


class MaxPlus(base.Semiring):

    def __init__(self, score, d):
        self.score = score
        self.d = d

    def __add__(self, other):
        if other is MaxPlus.zero: return self
        if self is MaxPlus.zero: return other
        if self.score >= other.score:
            return self
        else:
            return other

    def __mul__(self, other):
        if other is MaxPlus.one: return self
        if self is MaxPlus.one: return other
        return MaxPlus(self.score + other.score, (self, other))

    def __lt__(self, other):
        return self.score < other.score

    def __repr__(self):
        return f'MaxPlus({self.score}, {self.d})'


MaxPlus.zero = MaxPlus(float('-inf'), None)
MaxPlus.one = MaxPlus(0.0, ())
