"""
Unfolding the hidden computations of the second order expectation semiring
with this inside-outside trick.
"""

from hypergraphs.hypergraph import Hypergraph
from hypergraphs.semirings.logval import LogVal, LogValVector
from collections import defaultdict


def inside(g, zero):
    "Run inside algorithm on hypergraph `g` in a given semiring."
    B = defaultdict(zero)
    for x in g.toposort():
        for e in g.incoming[x]:
            v = zero()
            v.p = e.weight.p
            v.r = e.weight.r
            for b in e.body:
                v.r = v.p * B[b].r + B[b].p * v.r
                v.p = v.p * B[b].p
            B[x].r += v.r
            B[x].p += v.p
    return B


def outside(g, B, zero, one):
    "Run outside algorithm on hypergraph `g` in a given semiring."
    A = defaultdict(zero)
    A[g.root] = one()
    for v in reversed(list(g.toposort())):
        for e in g.incoming[v]:
            for u in e.body:
                z = zero()
                z.r = e.weight.p * A[v].r + A[v].p * e.weight.r
                z.p = A[v].p * e.weight.p
                for w in e.body:
                    if w != u:
                        z.r = z.p * B[w].r + B[w].p * z.r
                        z.p = z.p * B[w].p
                A[u].r += z.r
                A[u].p += z.p
    return A


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

    B = inside(g, zero=ExpectationSemiring.zero)
    A = outside(g, B, zero=ExpectationSemiring.zero, one=ExpectationSemiring.one)

    # The (s,t) component is an efficient linear combination with coefficients
    # from the cheap semiring.
    xs = LogValVector()
    xt = LogValVector()

    for e, (p,r,s) in E.items():
        x = e[0]
        kebar = ExpectationSemiring.zero()
        kebar.p = A[x].p
        kebar.r = A[x].r
        for u in e[1:]:
            kebar.r = B[u].p*kebar.r + kebar.p*B[u].r
            kebar.p *= B[u].p
        xs += s*p*kebar.p
        xt += s*p*(r * kebar.p + kebar.r)

    return (B[g.root].p, B[g.root].r, xs, xt)


class ExpectationSemiring(object):
    def __init__(self, p, r):
        self.p = p
        self.r = r
    @classmethod
    def zero(cls):
        return cls(LogVal.zero(), LogVal.zero())
    @classmethod
    def one(cls):
        return cls(LogVal.one(), LogVal.zero())
    def __repr__(self):
        return '(%s,%s)' % (self.p, self.r)
