from hypergraphs.hypergraph import Hypergraph
from hypergraphs.logval import LogVal, LogValVector


def inside_outside_speedup(E, root):
    """Inside-outside speed-up for computing second-order expectations on a
    hypergraph.

    """
    # Perform inside-outside in the "cheap" semiring.
    g = Hypergraph()
    g.root = root
    for e, (p,r,_) in E.items():
        ke = ExpectationSemiring(p, p*r)
        g.edge(ke, *e)

    B = g.inside(zero=ExpectationSemiring.Zero)
    A = g.outside(B, zero=ExpectationSemiring.Zero, one=ExpectationSemiring.One)

    # The (s,t) component is an efficient linear combination with coefficients
    # from the cheap semiring.
    xhat = AccumulatorModule.Zero()
    for e, (p,r,s) in E.items():
        kebar = A[e[0]]
        for u in e[1:]:
            kebar *= B[u]
        xhat += AccumulatorModule(p*s, p*r*s) * kebar  # left-multiplication

    return (B[g.root], xhat)


class ExpectationSemiring(object):
    def __init__(self, p, r):
        self.p = p
        self.r = r
    def __add__(self, x):
        return ExpectationSemiring(self.p + x.p, self.r + x.r)
    def __mul__(self, x):
        return ExpectationSemiring(self.p * x.p, self.p * x.r + x.p * self.r)
    @classmethod
    def Zero(cls):
        return cls(LogVal.Zero(), LogVal.Zero())
    @classmethod
    def One(cls):
        return cls(LogVal.One(), LogVal.Zero())
    def __repr__(self):
        return '(%s,%s)' % (self.p, self.r)


class AccumulatorModule(object):
    def __init__(self, s, t):
        self.s = s
        self.t = t
    @classmethod
    def Zero(cls):
        return cls(LogValVector.Zero(), LogValVector.Zero())
    def __add__(self, x):
        return AccumulatorModule(self.s + x.s,
                                 self.t + x.t)
    def __mul__(self, x):
        assert isinstance(x, ExpectationSemiring)
        return AccumulatorModule(self.s * x.p,
                                 self.t * x.p + self.s * x.r)
