from collections import defaultdict

from numpy import log as _log, exp, isnan, log1p as _log1p, expm1
from arsenal import colors
from arsenal.maths import log1pexp, log1mexp


def log(x):
    if x <= 0:
        return float('-inf')
    return _log(x)


def log1p(x):
    if x <= -1:
        return float('-inf')
    return _log1p(x)


from hypergraphs.semirings import base
class LogVal(base.Semiring):

    def __init__(self, pos, ell):
        self.pos = pos
        self.ell = ell

    @classmethod
    def lift(cls, x):
        return cls(x >= 0, log(abs(x)))

    def __lt__(self, other):
        return float(self) < float(other)

    def is_zero(self):
        return self.ell <= float('-inf')

    def to_real(self):
        if self.is_zero():
            return 0.0
        elif self.pos:
            return +float(exp(self.ell))
        else:
            return -float(exp(self.ell))

    lower = to_real
    __float__ = to_real

    def __mul__(self, b):
        if not isinstance(b, LogVal):
            return b * self
        c = LogVal.lift(0.0)
        if self.is_zero() or b.is_zero():
            return c
        c.pos = self.pos == b.pos
        c.ell = self.ell + b.ell
        return c

    def __neg__(self):
        return LogVal(pos=(not self.pos), ell=self.ell)

    def __truediv__(self, b):
        c = LogVal.lift(0.0)
        if self.is_zero():
            return c
        if b.is_zero():
            return c         # divide by zero: Should probably return NaN.
        c.pos = self.pos == b.pos
        c.ell = self.ell - b.ell
        return c

    __div__ = __truediv__

    def __sub__(self, b):
        c = LogVal.lift(0.0)
        c.ell = b.ell
        c.pos = not b.pos
        return self + c

    def __add__(self, b):
        c = LogVal.lift(0.0)
        a = self
        if a.ell < b.ell:
            a, b = b, a
        if a.is_zero():
            c.pos = b.pos
            c.ell = b.ell
            return c
        if b.is_zero():
            c.pos = a.pos
            c.ell = a.ell
            return c
        x = b.ell - a.ell
        assert not isnan(x)
#        assert x <= 0         # unnecessary assertion.
        if a.pos == 1 and b.pos == 1:
            c.pos = 1
            c.ell = a.ell + log1pexp(x)   # log(1+exp(x))
        elif a.pos == 1 and b.pos == 0:
            c.pos = 1
            c.ell = a.ell + log1mexp(x)   # log(1-exp(x))
        elif a.pos == 0 and b.pos == 1:
            c.pos = 0
            c.ell = a.ell + log1mexp(x)
        else:
            c.pos = 0
            c.ell = a.ell + log1pexp(x)
        return c

    def __repr__(self):
#        return 'LogVal(%g)' % self.to_real()
        x = self.to_real()
        sign = '+' if self.pos else colors.cyan % '-'
        if x > 1.000001 or x < -0.00001:
            return 'LogVal(%s=%sexp(%g))' % (colors.red % x, sign, self.ell)
        else:
            return 'LogVal(%g=%sexp(%g))' % (x, sign, self.ell)

LogVal.zero = LogVal.lift(0.0)
LogVal.one = LogVal.lift(1.0)


from hypergraphs.semirings.vector import make_vector
LogValVector = make_vector(LogVal)
