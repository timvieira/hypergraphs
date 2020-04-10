class Count:

    def __init__(self, x):
        assert isinstance(x, int)
        self.x = x

    @classmethod
    def lift(cls, x):
        return cls(x)

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

    @classmethod
    def zero(cls):
        return cls(0)

    @classmethod
    def one(cls):
        return cls(1)

    def __repr__(self):
        return f'Count({self.x})'
