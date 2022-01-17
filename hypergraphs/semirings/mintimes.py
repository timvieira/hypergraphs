from hypergraphs.semirings import base

class MinTimes(base.Semiring):

    def __init__(self, cost, d):
        self.cost = cost
        self.d = d

    def __add__(self, other):
        return min(self, other)

    def __mul__(self, other):
        if other is one: return self
        if self is one: return other
        if self is zero: return zero
        if other is zero: return zero
        return MinTimes(self.cost * other.cost, (self.d, other.d))

    def __lt__(self, other):
        return self.cost < other.cost

    def __repr__(self):
        return f'MinTimes({self.cost}, {self.d})'

    @classmethod
    def multiplicity(cls,x,m):
        if m > 0:
            return x
        else:
            return cls.zero

    def __eq__(self, other):
        return self.cost == other.cost and self.d == other.d

    def __hash__(self):
        return hash((self.cost, self.d))

MinTimes.zero = zero = MinTimes(float('inf'), None)
MinTimes.one = one = MinTimes(1, ())
