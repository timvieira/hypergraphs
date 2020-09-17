import numpy as np
from hypergraphs.semirings import base


class Expon(base.Semiring):

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
        xs,xd = x.value
        ys,yd = y.value

        self.value = (self.value, [xd, yd])

        # Neither of these options work
#        self.value = (xs/y.w, [xd, yd])
#        self.value = (min(xs/y.w, ys/x.w), [xd, yd])



zero = Expon(0.0, None)
one = Expon(1.0, ())

Expon.zero = zero
Expon.one = one
