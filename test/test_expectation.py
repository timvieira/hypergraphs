import numpy as np
from hypergraphs.semirings.logval import LogVal, LogValVector
from hypergraphs.hypergraph import Hypergraph
from hypergraphs.semirings import Expectation, SecondOrderExpectation
from nltk import ImmutableTree as Tree
#from hypergraphs.alg.insideout import inside_outside_speedup
#from hypergraphs.alg import insideout
#from ldp.parsing.util import tree_edges


def is_terminal(d):
    return not isinstance(d, Tree)

def tree_edges(t):
    """
    Extract hyperedges from a tree (derivation).

    >>> for x in tree_edges(Tree.fromstring('(A a (B b (C c)) d)')):
    ...     print x
    ('A', ['a', 'B', 'd'])
    ('B', ['b', 'C'])
    ('C', ['c'])

    """
    if is_terminal(t):
        return []
    return [(s.label(), [b.label() if isinstance(b, Tree) else b for b in s]) for s in t.subtrees()]


def secondorder_graph(E, root):
    # Build hypergraph from edge set (no enumeration over derivations required)
    g = Hypergraph()
    g.root = root

    # For computing risk using the second-order expectation semiring we set the
    # edge weights as follows: k_e = (p, p*r, p*s p*r*s). Note: the equivalent
    # computation in the brute-force setting does not do this transformation.
    for e, (p,r,s) in E.items():
        ke = SecondOrderExpectation(p, p*r, p*s, p*r*s)
        g.edge(ke, *e)

    return g


def firstorder_graph(E, root):
    # Build hypergraph from edge set (no enumeration over derivations required)
    g = Hypergraph()
    g.root = root

    # For computing risk using the second-order expectation semiring we set the
    # edge weights as follows: k_e = (p, p*r, p*s p*r*s). Note: the equivalent
    # computation in the brute-force setting does not do this transformation.
    for e, (p,r,s) in E.items():
        ke = Expectation(p, p*r)
        ke.s = s
        g.edge(ke, *e)

    return g



def brute_force(derivations, E):
    "Brute-force enumeration method for computing (Z, rbar, sbar, tbar)."
    Z = LogVal.zero
    rbar = LogVal.zero
    sbar = LogValVector()
    tbar = LogValVector()
    for d in derivations:
        #print
        #print 'Derivation:', d
        rd = LogVal.zero
        pd = LogVal.one
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
    return SecondOrderExpectation(Z, rbar, sbar, tbar)


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


#def fdcheck(E, root, eps=1e-4):
#    """Finite-difference approximation of gradient of numerator and denominator wrt
#    edge probability.
#
#    """
#
#    def fn(W):
#        "Evaluate numerator and denominator of risk."
#        g = Hypergraph()
#        g.root = root
#        for e,[_,r,f] in list(E.items()):
#            p = LogVal.lift(np.exp((f @ W).to_real()))
#            g.edge(Expectation(p, p*r), *e)
#        B = g.inside()
#        Q = B[g.root]
#        return Q.p.to_real(), Q.r.to_real(), (Q.r/Q.p).to_real()
#
#    features = {k for [_,_,f] in E.values() for k in f}
#    W = LogValVector({k: LogVal.lift(np.random.uniform(-1,1)) for k in features})
#
#    # For gradient of risk we use <p, p*r, D[p], r*D[p]>, but my code computes
#    # <p, p*r, p*s, p*r*s>, so we pass in s=D[p]/p.
#    #
#    # D[p] = D[exp(f @ W))] = exp(s @ W))*D[f @ W] = exp(s @ W)*f
#    #
#    # therefore D[p]/p = f
#    E1 = {}
#    for e,[_,r,f] in list(E.items()):
#        p = LogVal.lift(np.exp((f @ W).to_real()))
#        E1[e] = (p,r,f)
#
#
#    sog = secondorder_graph(E, root)
#    khat, xhat = sog.insideout()
#
#    ad_Z = xhat.s
#    ad_rbar = xhat.t
#    Z = khat.p
#    rbar = khat.r
#
#    ad_risk = ad_rbar/Z - rbar*ad_Z/Z/Z
#
#    dd = []
#    for k in features:
#        was = W[k]
#        W.x[k] = was + LogVal.lift(eps)
#        b_Z, b_rbar, b_risk = fn(W)
#        W.x[k] = was - LogVal.lift(eps)
#        a_Z, a_rbar, a_risk = fn(W)
#        W.x[k] = was
#
#        fd_rbar = (b_rbar - a_rbar)/(2*eps)
#        fd_Z    = (b_Z    - a_Z   )/(2*eps)
#        fd_risk = (b_risk - a_risk)/(2*eps)
#
#        dd.append({'key':     k,
#                   'ad_risk': ad_risk[k].to_real(),
#                   'fd_risk': fd_risk,
#                   'ad_Z':    ad_Z[k].to_real(),
#                   'fd_Z':    fd_Z,
#                   'ad_rbar': ad_rbar[k].to_real(),
#                   'fd_rbar': fd_rbar})
#
#    from pandas import DataFrame
#    df = DataFrame(dd)
#    #from arsenal.maths import compare
#    #compare(df.fd_Z, df.ad_Z, alphabet=df.key).show()
#    #compare(df.fd_rbar, df.ad_rbar, alphabet=df.key).show()
#    #compare(df.fd_risk, df.ad_risk, alphabet=df.key).show()
#    assert np.allclose(df.fd_Z, df.ad_Z)
#    assert np.allclose(df.fd_rbar, df.ad_rbar)
#    assert np.allclose(df.fd_risk, df.ad_risk)
#    #import pylab as pl; pl.show()
#    print('[fdcheck] ok')


def test():

    root, D, E = small()
#    fdcheck(E, root)

    b = brute_force(D, E)
    dump(b)

    sog = secondorder_graph(E, root)
    Q = sog.inside()[root]
    dump(Q)
    check_equal(Q, b)


    # TODO: [2020-10-20 Tue] insideout speedup is failing.
    if 1:
        from hypergraphs.semirings.vector import make_vector
        V = make_vector(Expectation)

        fog = firstorder_graph(E, root)
        B = fog.inside()
        A = fog.outside(B)
        def X(e):
            p,r,s = e.weight.p, e.weight.r, e.weight.s
            return Expectation(p*s, p*r*s)

        khat, xhat = fog.insideout(B, A, X, V.zero)
        v = SecondOrderExpectation(khat.p, khat.r, xhat.s, xhat.t)

        dump(v)
        check_equal(Q, v)


if __name__ == '__main__':
    test()
