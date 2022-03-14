from hypergraphs.semirings import base


class MinTimes(base.Semiring):

    def __init__(self, cost, d=None):
        self.cost = cost
        self.d = d

    def __repr__(self):
        return f'MinTimes({self.cost}, {self.d})'

    def __eq__(self, other):
        return isinstance(other, MinTimes) and self.cost == other.cost

    def __hash__(self):
        return hash(self.cost)

    @classmethod
    def samples(cls):
        return [
            cls(float('+inf')),
            cls.zero,
            cls.one,
            cls(+3),
            cls(2),
            cls(2.18),
        ]

    def __lt__(self, other):
        return isinstance(other, MinTimes) and self.cost < other.cost

    def __add__(self, other):
        return min(self, other)

    def __mul__(self, other):
        if other is one: return self
        if self is one: return other
        if self is zero: return zero
        if other is zero: return zero
        return MinTimes(self.cost * other.cost, (self.d, other.d))

    @classmethod
    def multiplicity(cls,x,m):
        if m > 0:
            return x
        else:
            return cls.zero

    def star(self):
        if self.cost < 0: return MinTimes(float('-inf'), None)
        return self.one + self


MinTimes.zero = zero = MinTimes(float('inf'), None)
MinTimes.one = one = MinTimes(1, ())
