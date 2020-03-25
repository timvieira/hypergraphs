"""
Second-order expectation semiring (Li & Eisner, 2009).
"""

from hypergraphs.semirings.logval import LogVal, LogValVector


class Semiring2:
    """Second-order Expectation Semiring.

    Note: We don't recommend using this implementation. For most computations
    the inside-outside speed-up will be more efficient and less memory
    intensive.

    """

    def __init__(self, p, r, s, t):
        self.p = p
        self.r = r
        self.s = s
        self.t = t

    @classmethod
    def zero(cls):
        return cls(LogVal.zero(),
                   LogVal.zero(),
                   LogValVector(),
                   LogValVector())

    def __repr__(self):
        return repr((self.p, self.r, self.s, self.t))

    @staticmethod
    def one():
        return Semiring2(LogVal.one(),
                         LogVal.zero(),
                         LogValVector(),
                         LogValVector())

    def __add__(self, y):
        return Semiring2(self.p + y.p,
                         self.r + y.r,
                         self.s + y.s,
                         self.t + y.t)

    def __mul__(self, y):
        p1,r1,s1,t1 = self.p, self.r, self.s, self.t
        p2,r2,s2,t2 = y.p, y.r, y.s, y.t
        return Semiring2(p1*p2,
                         p1*r2 + p2*r1,
                         p1*s2 + p2*s1,
                         p1*t2 + p2*t1 + r1*s2 + r2*s1)


class Semiring1:
    """
    First-order Expectation Semiring.
    """

    def __init__(self, p, r):
        self.p = p
        self.r = r

    @classmethod
    def zero(cls):
        return cls(LogVal.zero(),
                   LogVal.zero())

    def __repr__(self):
        return repr((self.p, self.r, self.s, self.t))

    @staticmethod
    def one():
        return Semiring1(LogVal.one(),
                         LogVal.zero())

    def __add__(self, y):
        return Semiring1(self.p + y.p,
                         self.r + y.r)

    def __mul__(self, y):
        p1,r1 = self.p, self.r
        p2,r2 = y.p, y.r
        return Semiring1(p1*p2,
                         p1*r2 + p2*r1)
