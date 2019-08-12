from collections import defaultdict

from numpy import log as _log, exp, isnan, log1p as _log1p, expm1
from arsenal import colors


def log(x):
    if x <= 0:
        return float('-inf')
    return _log(x)


def log1p(x):
    if x <= -1:
        return float('-inf')
    return _log1p(x)


def log1pexp(x):
    """
    Numerically stable implementation of log(1+exp(x)) aka softmax(0,x).

    -log1pexp(-x) is log(sigmoid(x))

    Source:
    http://cran.r-project.org/web/packages/Rmpfr/vignettes/log1mexp-note.pdf
    """
    if x <= -37:
        return exp(x)
    elif -37 <= x <= 18:
        return log1p(exp(x))
    elif 18 < x <= 33.3:
        return x + exp(-x)
    else:
        return x


def log1mexp(x):
    """
    Numerically stable implementation of log(1-exp(x))

    Source:
    http://cran.r-project.org/web/packages/Rmpfr/vignettes/log1mexp-note.pdf
    """
    assert x <= 0
    a = abs(x)
    if 0 < a <= 0.693:
        return log(-expm1(-a))
    else:
        return log1p(-exp(-a))


class LogVal:

    def __init__(self, a):
        self.pos = a >= 0
        self.ell = log(abs(a))

    def logeq(self, x):
        assert x <= 0, x
        self.pos = 1
        self.ell = x

    def is_zero(self):
        return self.ell <= float('-inf')

    def to_real(self):
        if self.is_zero():
            return 0.0
        elif self.pos:
            return +float(exp(self.ell))
        else:
            return -float(exp(self.ell))

    def __mul__(self, b):
        if not isinstance(b, LogVal):
            return b * self
        c = LogVal(0.0)
        if self.is_zero() or b.is_zero():
            return c
        c.pos = self.pos == b.pos
        c.ell = self.ell + b.ell
        return c

    def __truediv__(self, b):
        c = LogVal(0.0)
        if self.is_zero():
            return c
        if b.is_zero():
            return c         # divide by zero: Should probably return NaN.
        c.pos = self.pos == b.pos
        c.ell = self.ell - b.ell
        return c

    __div__ = __truediv__

    def __sub__(self, b):
        c = LogVal(0.0)
        c.ell = b.ell
        c.pos = not b.pos
        return self + c

    def __add__(self, b):
        c = LogVal(0.0)
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

    @staticmethod
    def Zero():
        return LogVal(0.0)

    @staticmethod
    def One():
        return LogVal(1.0)

    def __repr__(self):
#        return 'LogVal(%g)' % self.to_real()
        x = self.to_real()
        sign = '+' if self.pos else colors.cyan % '-'
        if x > 1.000001 or x < -0.00001:
            return 'LogVal(%s=%sexp(%g))' % (colors.red % x, sign, self.ell)
        else:
            return 'LogVal(%g=%sexp(%g))' % (x, sign, self.ell)


class LogValVector(object):
    def __init__(self, vals=None):
        self.x = defaultdict(LogVal.Zero)
        if vals is not None:
            self.x.update(vals)
    @classmethod
    def Zero(cls):
        return cls()
    def __mul__(self, x):
        assert isinstance(x, LogVal), x
        c = LogValVector()
        for k,v in self.x.items():
            c.x[k] = v*x
        return c
    def __truediv__(self, x):
        assert isinstance(x, LogVal), x
        c = LogValVector()
        for k,v in self.x.items():
            c.x[k] = v/x
        return c
    __div__ = __truediv__
    def __sub__(self, x):
        return self + LogVal(-1)*x
    def dot(self, w):
        v = LogVal.Zero()
        for k in self:
            v += self[k]*w[k]
        return v
    def __add__(self, x):
#        assert isinstance(x, LogValVector), x
        c = LogValVector()
        for k,v in self.x.items():
            c.x[k] += v
        for k,v in x.x.items():
            c.x[k] += v
        return c
    def is_zero(self):
        return all(y.is_zero() for y in self.x.values())
    def __repr__(self):
        return 'LogValVector(%r)' % dict(self.x)
    def __str__(self):
        return 'LogValVector({\n%s\n})' % '\n'.join('  %r: %r,' % (k,v) for k,v in sorted(self.x.items()))
    def __getitem__(self, key):
        return self.x[key]
    def to_real(self):
        x = defaultdict(float)
        for k,v in self.x.items():
            x[k] = v.to_real()
        return x
    def __iter__(self):
        return iter(self.x)
