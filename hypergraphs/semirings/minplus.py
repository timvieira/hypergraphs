from hypergraphs.semirings import base


class MinPlus(base.Semiring):

    def __init__(self, cost, d):
        self.cost = cost
        self.d = d

    def __add__(self, other):
        if other is zero: return self
        if self is zero: return other
        if self.cost <= other.cost:
            return self
        else:
            return other

    def __mul__(self, other):
        if other is one: return self
        if self is one: return other
        return MinPlus(self.cost + other.cost, (self.d, other.d))

    def __lt__(self, other):
        return self.cost < other.cost

    def __repr__(self):
        return f'MinPlus({self.cost}, {self.d})'

    @classmethod
    def multiplicity(cls,x,m):
        if m > 0:
            return x
        else:
            return cls.zero


MinPlus.zero = zero = MinPlus(float('inf'), None)
MinPlus.one = one = MinPlus(0.0, ())
