import numpy as np
import pylab as pl
from arsenal import iterview
from arsenal.maths import random_dist, compare

from semirings import MaxPlus
from hypergraphs.apps.parser2 import parse, load_grammar


def parser(sentence, grammar, w, Weights):
    def binary(sentence,X,Y,Z,i,j,k):
        return Weights(w(X,Y,Z,i,j,k), X)
    def unary(sentence,X,Y,i,k):
        return Weights(w(X,Y,i,k), X)
    def terminal(sentence,W,i):
        return Weights(1.0, W)
    return parse(sentence, grammar, binary, unary, terminal, zero = Weights.zero)[0,len(sentence),'S']


def test_parse():
    from arsenal.cache import memoize
    from semirings import LazySort

#    w = memoize(lambda *edge: np.exp(np.random.randn()))
    w = memoize(lambda *edge: np.random.uniform())

#    sentence = 'Papa ate the caviar with the spoon .'.split()
    sentence = 'Papa ate the caviar .'.split()

    grammar = load_grammar("""
    S       X .
    X       X X
    X       Papa
    X       ate
    X       the
    X       caviar
    X       with
    X       spoon
    X       in
    X       park
    """)


    def distribution():
        root = parser(sentence, grammar, w, LazySort)
        Z = 0.0
        p = {}
        for x in root:
            p[str(x.data)] = x.score
            Z += x.score
        return normalize(p)

    p = distribution()

    for x in p:
        print(p[str(x)], x)

    # TODO: make the parser return a the root rather than the full chart.
    q = {x: 0 for x in p}
    reps = 10_000


    if 1:
        # [2020-10-30 Fri] can we just perturb the edge weights and take the
        # max?  These experiments don't appear to confirm that... Has someone
        # proved that it is possible?
        def G(): return -np.log(-np.log(np.random.uniform(0,1)))
        def sample():
            g = {e: G() for e in w.cache}
            def wg(*e): return np.log(w.cache[e]) + g[e]
            return parser(sentence, grammar, wg, MaxPlus).d

    else:
        from semirings.sampling.lazy2 import Sample
        sampler = iter(parser(sentence, grammar, w, Sample))
        def sample(): return next(sampler)[1]


    from arsenal.viz import lc
    lc = lc['mc'].loglog()
    for r in iterview(range(1, 1+reps)):
        s = sample()
        q[str(s)] += 1

        if r % 1_000 == 0:
            err = 0.5*sum(abs(p[x] - q[x]/r) for x in p)

            print(f'\nerr({r})=', err)
            #lc.update(r, err=err)


            for x in p:
                print(abs(p[str(x)] - q[str(x)]/r), p[str(x)], q[str(x)]/r, x)
            print()


    q = normalize(q)

    compare(p, q)#.show()


def normalize(p):
    Z = sum(p.values())
    q = {}
    for x in p:
        q[x] = p[x]/Z
    return q


if __name__ == '__main__':
    test_parse()
