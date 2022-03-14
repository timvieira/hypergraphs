from collections import defaultdict


class Count:

    def __init__(self, x):
        assert isinstance(x, int)
        self.x = x

    @classmethod
    def lift(cls, x, d=None):
        return cls(x)

    @classmethod
    def chart(cls):
        return defaultdict(lambda: cls.zero)

    def __lt__(self, other):
        return self.x < other.x

    def lower(self):
        return self.x

    __float__ = lower

    def __mul__(self, b):
        return Count(self.x * b.x)

    def __sub__(self, b):
        return Count(self.x - b.x)

    def __add__(self, b):
        return Count(self.x + b.x)

    def __repr__(self):
        return f'Count({self.x})'


Count.zero = Count(0)
Count.one = Count(1)
