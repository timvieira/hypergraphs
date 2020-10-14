import numpy as np
from hypergraphs.semirings import base


class Sample(base.Semiring):

    def __init__(self, w, d):
        self.w = w
        self.d = d

    def sample(self):
        return (self.w, self.d)

    def __iter__(self):
        while True:
            yield self.sample()

    def __add__(self, other):
        if other is zero: return self
        if self is zero: return other
        return Sum(self, other)

    def __mul__(self, other):
        if other is one: return self
        if self is one: return other
        if other is zero: return zero
        if self is zero: return zero
        return Prod(self, other)

    @staticmethod
    def star(x):
        return Star(x)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.w}, {self.d})'


class Sum(Sample):
    def __init__(self, x, y):
        self.x = x; self.y = y
        super().__init__(x.w + y.w, d=[x,y])
    def sample(self):
        if np.random.uniform(0, 1) * (self.x.w + self.y.w) <= self.x.w:
            return self.x.sample()
        else:
            return self.y.sample()


class Prod(Sample):
    def __init__(self, x, y):
        self.x = x; self.y = y
        super().__init__(x.w * y.w, d=[x,y])
    def sample(self):
        xs,xd = self.x.sample()
        ys,yd = self.y.sample()
        return [xs*ys, [xd, yd]]


class Star(Sample):
    def __init__(self, x):
        self.x = x
        super().__init__(1/(1-x.w), d=[x])
    def sample(self):
        # sample a number of repetitions for a geometric distribution
        zs = 1
        zd = []
        while True:
            if np.random.uniform() <= self.x.w:
                xs, xd = self.x.sample()
                zs = zs*xs
                zd = [zd, xd]
            else:
                return zs, zd


zero = Sample(0.0, None)
one = Sample(1.0, ())


Sample.one = one
Sample.zero = zero
