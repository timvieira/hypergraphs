"""
Second-order expectation semiring (Li & Eisner, 2009).
"""

from hypergraphs.semirings.logval import LogVal, LogValVector

# TODO: cleaner construction by nesting
#def SecondOrderExpectation(p,r,s,t):
#    "Second-order Expectation Semiring by nesting."
#    return Expectation(Expectation(p, r), Expectation(s, t))

# TODO: switch to "meta" semirings: the expectation semiring (first and second)
# can be constructed out of more basic semirings (thats were the zero and one
# elements come from).  This will avoid the hard coded LogVal.zero stuff below.

from hypergraphs.semirings import base

class SecondOrderExpectation(base.Semiring):
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

    def __repr__(self):
        return repr((self.p, self.r, self.s, self.t))

    def __add__(self, y):
        return SecondOrderExpectation(self.p + y.p,
                                      self.r + y.r,
                                      self.s + y.s,
                                      self.t + y.t)

    def __mul__(self, y):
        p1,r1,s1,t1 = self.p, self.r, self.s, self.t
        p2,r2,s2,t2 = y.p, y.r, y.s, y.t
        return SecondOrderExpectation(p1*p2,
                                      p1*r2 + p2*r1,
                                      p1*s2 + p2*s1,
                                      p1*t2 + p2*t1 + r1*s2 + r2*s1)


SecondOrderExpectation.zero = SecondOrderExpectation(LogVal.zero,
                                                     LogVal.zero,
                                                     LogValVector(),
                                                     LogValVector())
SecondOrderExpectation.one = SecondOrderExpectation(LogVal.one,
                                                    LogVal.zero,
                                                    LogValVector(),
                                                    LogValVector())

def make_expectation(P, R):

    class Expectation(base.Semiring):
        """
        First-order Expectation Semiring.
        """

        def __init__(self, p, r):
            self.p = p
            self.r = r

        def __repr__(self):
            return repr((self.p, self.r))

        def __add__(self, y):
            return Expectation(self.p + y.p,
                               self.r + y.r)

        def __mul__(self, y):
            p1,r1 = self.p, self.r
            p2,r2 = y.p, y.r
            return Expectation(p1*p2,
                               p1*r2 + p2*r1)

    Expectation.zero = Expectation(P.zero, R.zero)
    Expectation.one = Expectation(P.one, R.zero)

    return Expectation

Expectation = make_expectation(LogVal, LogVal)
