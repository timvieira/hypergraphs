from hypergraphs.hypergraph import Hypergraph
from hypergraphs.logval import LogVal, LogValVector


def inside_outside_speedup(E, root):
    """Inside-outside speed-up for computing second-order expectations on a
    hypergraph.

    This version is for k=<p,p*r,s,s*r>, not k=<p,p*r,p*s,p*s*r>.

    Edge weights if the support form are used from computing gradient of risk.

    Where s = D[p]. If you don't use this trick then you have to use D[p]/p,
    which is problematic for p=0.

    """
    # Perform inside-outside in the "cheap" semiring.
    g = Hypergraph()
    g.root = root
    for e, (p,r,_) in E.items():
        ke = ExpectationSemiring(p, p*r)
        g.edge(ke, *e)

    B = g.inside(zero=ExpectationSemiring.zero)
    A = g.outside(B, zero=ExpectationSemiring.zero, one=ExpectationSemiring.one)

    # The (s,t) component is an efficient linear combination with coefficients
    # from the cheap semiring.
    xhat = AccumulatorModule.zero()
    for e, (p,r,s) in E.items():
        kebar = A[e[0]]
        for u in e[1:]:
            kebar *= B[u]
        xhat += AccumulatorModule(s, r*s) * kebar  # left-multiplication

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
    def zero(cls):
        return cls(LogVal.zero(), LogVal.zero())
    @classmethod
    def one(cls):
        return cls(LogVal.one(), LogVal.zero())
    def __repr__(self):
        return '(%s,%s)' % (self.p, self.r)


class AccumulatorModule(object):
    def __init__(self, s, t):
        self.s = s
        self.t = t
    @classmethod
    def zero(cls):
        return cls(LogValVector.zero(), LogValVector.zero())
    def __add__(self, x):
        return AccumulatorModule(self.s + x.s,
                                 self.t + x.t)
    def __mul__(self, x):
        assert isinstance(x, ExpectationSemiring)
        return AccumulatorModule(self.s * x.p,
                                 self.t * x.p + self.s * x.r)
