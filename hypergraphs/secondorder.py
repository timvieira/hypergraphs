"""
Second-order expectation semiring (Li & Eisner, 2009).
"""

import numpy as np
from hypergraphs.hypergraph import Hypergraph
from hypergraphs.logval import LogVal, LogValVector
from ldp.parsing.util import tree_edges
from nltk import ImmutableTree as Tree


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


def secondorder_expectation_semiring(E, root):
    # Build hypergraph from edge set (no enumeration over derivations required)
    g = Hypergraph()
    g.root = root

    # For computing risk using the second-order expectation semiring we set the
    # edge weights as follows: k_e = (p, p*r, p*s p*r*s). Note: the equivalent
    # computation in the brute-force setting does not do this transformation.
    for e, (p,r,s) in E.items():
        ke = Semiring2(p, p*r, p*s, p*r*s)
        g.edge(ke, *e)

    # Inside algorithm for computing the same stuff as above more efficiently.
    B = g.inside(zero=Semiring2.zero)
    return B[g.root]


def brute_force(derivations, E):
    "Brute-force enumeration method for computing (Z, rbar, sbar, tbar)."
    Z = LogVal.zero()
    rbar = LogVal.zero()
    sbar = LogValVector()
    tbar = LogValVector()
    for d in derivations:
        #print
        #print 'Derivation:', d
        rd = LogVal.zero()
        pd = LogVal.one()
        sd = LogValVector()
        for [x,[y,z]] in tree_edges(d):
            (p,r,s) = E[x,y,z]
            #print (x,y,z), tuple(x.to_real() for x in (p, r, s))
            pd *= p
            rd += r
            sd += s
        #print 'p=%s,r=%s,s=%s' % tuple(x.to_real() for x in (pd, rd, sd))
        Z += pd
        rbar += pd*rd
        sbar += pd*sd
        tbar += pd*rd*sd
    return Semiring2(Z, rbar, sbar, tbar)


def small():

    # Define the set of valid derivations.
    D = [
        Tree('(0,3)', [Tree('(0,2)', ['(0,1)', '(1,2)']), '(2,3)']),
        Tree('(0,3)', ['(0,1)', Tree('(1,3)', ['(1,2)', '(2,3)'])]),
    ]

    # Define the set of edges and the associated (p,r,s) values that are local
    # to each edge.
    E = {
        ('(0,3)', '(0,2)', '(2,3)'): (
            LogVal.lift(10),
            LogVal.lift(1),
            LogValVector({'023': LogVal.lift(1), '23': LogVal.lift(1)}),
        ),
        ('(0,2)', '(0,1)', '(1,2)'): (
            LogVal.lift(10),
            LogVal.lift(1),
            LogValVector({'012': LogVal.lift(1)}),
        ),
        ('(0,3)', '(0,1)', '(1,3)'): (
            LogVal.lift(20),
            LogVal.lift(1),
            LogValVector({'013': LogVal.lift(1)}),
        ),
        ('(1,3)', '(1,2)', '(2,3)'): (
            LogVal.lift(10),
            LogVal.lift(3),
            LogValVector({'123': LogVal.lift(1), '23': LogVal.lift(1)}),
        ),
        ('(0,1)',): (LogVal.lift(1), LogVal.lift(0), LogValVector()),
        ('(1,2)',): (LogVal.lift(1), LogVal.lift(0), LogValVector()),
        ('(2,3)',): (LogVal.lift(1), LogVal.lift(0), LogValVector()),
    }

    # Define the root of all derivations hypergraph.
    root = '(0,3)'

    assert all(d.label() == root for d in D), \
        'All derivations must have a common root node.'

    assert all(isinstance(k, tuple) for k in E)

    return root, D, E


def dump(b):
    print('r = %s (Z=%s, rbar=%s)' % tuple(x.to_real() for x in (b.r/b.p, b.p, b.r)))
    print('s =', dict((b.s/b.p).to_real()))
    print('t =', dict((b.t/b.p).to_real()))


def check_equal(Q, B):
    assert abs((Q.p - B.p).to_real()) < 1e-8
    assert abs((Q.r - B.r).to_real()) < 1e-8
    for k in set(Q.s)|set(B.s):
        assert abs((Q.s[k] - B.s[k]).to_real()) < 1e-8
    for k in set(Q.t)|set(B.t):
        assert abs((Q.t[k] - B.t[k]).to_real()) < 1e-8


def fdcheck(E, root, eps=1e-4):
    """Finite-difference approximation of gradient of numerator and denominator wrt
    edge probability.

    """

    def fn(W):
        "Evaluate numerator and denominator of risk."
        g = Hypergraph()
        g.root = root
        for e,[_,r,f] in list(E.items()):
            p = LogVal.lift(np.exp(f.dot(W).to_real()))
            g.edge(Semiring1(p, p*r), *e)
        B = g.inside(Semiring1.zero)
        Q = B[g.root]
        return Q.p.to_real(), Q.r.to_real(), (Q.r/Q.p).to_real()

    features = {k for [_,_,f] in E.values() for k in f}
    W = LogValVector({k: LogVal.lift(np.random.uniform(-1,1)) for k in features})

    # For gradient of risk we use <p, p*r, D[p], r*D[p]>, but my code computes
    # <p, p*r, p*s, p*r*s>, so we pass in s=D[p]/p.
    #
    # D[p] = D[exp(f.dot(W))] = exp(s.dot(W))*D[f.dot(W)] = exp(s.dot(W))*f
    #
    # therefore D[p]/p = f
    if 0:
        E1 = {}
        for e,[_,r,f] in list(E.items()):
            p = LogVal.lift(np.exp(f.dot(W).to_real()))
            E1[e] = (p,r,f*p)

        #S = secondorder_expectation_semiring(E, root)
        from hypergraphs.insideout3 import inside_outside_speedup
        khat, xhat = inside_outside_speedup(E1, root)

    else:
        E1 = {}
        for e,[_,r,f] in list(E.items()):
            p = LogVal.lift(np.exp(f.dot(W).to_real()))
            E1[e] = (p,r,f)

        #S = secondorder_expectation_semiring(E, root)
        from hypergraphs.insideout import inside_outside_speedup
        khat, xhat = inside_outside_speedup(E1, root)

    ad_Z = xhat.s
    ad_rbar = xhat.t
    Z = khat.p
    rbar = khat.r

    ad_risk = ad_rbar/Z - rbar*ad_Z/Z/Z

    dd = []
    for k in features:
        was = W[k]
        W.x[k] = was + LogVal.lift(eps)
        b_Z, b_rbar, b_risk = fn(W)
        W.x[k] = was - LogVal.lift(eps)
        a_Z, a_rbar, a_risk = fn(W)
        W.x[k] = was

        fd_rbar = (b_rbar - a_rbar)/(2*eps)
        fd_Z    = (b_Z    - a_Z   )/(2*eps)
        fd_risk = (b_risk - a_risk)/(2*eps)

        dd.append({'key':     k,
                   'ad_risk': ad_risk[k].to_real(),
                   'fd_risk': fd_risk,
                   'ad_Z':    ad_Z[k].to_real(),
                   'fd_Z':    fd_Z,
                   'ad_rbar': ad_rbar[k].to_real(),
                   'fd_rbar': fd_rbar})

    from arsenal.maths import compare
    from pandas import DataFrame
    df = DataFrame(dd)
    compare(df.fd_Z, df.ad_Z, alphabet=df.key).show()
    compare(df.fd_rbar, df.ad_rbar, alphabet=df.key).show()
    compare(df.fd_risk, df.ad_risk, alphabet=df.key).show()
    #import pylab as pl; pl.show()


def test():
    from hypergraphs import insideout, insideout2, enumeration

    root, D, E = small()

    fdcheck(E, root)

    derivations = set()
    for d in enumeration.enumerate_derivations(E, root).x:
        print(d)
        derivations.add(d)
    assert derivations == set(D), (derivations, set(D))

    b = brute_force(D, E)
    dump(b)

    Q = secondorder_expectation_semiring(E, root)

    dump(Q)
    check_equal(Q, b)

    khat, xhat = insideout.inside_outside_speedup(E, root)
    v = Semiring2(khat.p, khat.r, xhat.s, xhat.t)

    dump(v)
    check_equal(Q, v)

    x = insideout2.inside_outside_speedup(E, root)
    v = Semiring2(*x)

    dump(v)
    check_equal(Q, v)


if __name__ == '__main__':
    test()
