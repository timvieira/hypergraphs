import numpy as np


class Expon:

    def __init__(self, w, d):
        self.w = w
        self.d = d
        self.value = (-np.log(np.random.uniform(0,1)) / self.w if self.w != 0 else np.inf, d)

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

    def __repr__(self):
        return f'{self.__class__.__name__}({self.w}, {self.d})'

    @classmethod
    def zero(cls):
        return zero

    @classmethod
    def one(cls):
        return one


class Sum(Expon):
    def __init__(self, x, y):
        self.x = x; self.y = y

        # XXX: reuse x.value and y.value?
        super().__init__(x.w + y.w, d=[x,y])
        self.value = min(x.value, y.value)


class Prod(Expon):
    def __init__(self, x, y):
        self.x = x; self.y = y
        super().__init__(x.w * y.w, d=[x,y])

        # XXX: steal the backpointers, but take a fresh sample?
        _,xd = x.value
        _,yd = y.value

        self.value = (self.value, [xd, yd])


zero = Expon(0.0, None)
one = Expon(1.0, ())
