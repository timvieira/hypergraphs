import numpy as np
import pylab as pl
from arsenal import iterview
from arsenal.maths import random_dist, compare

from hypergraphs.apps.subsets import subsets


EAGER = False #True

if EAGER:
    from hypergraphs.semirings.sampling.eager import Expon as Sample
else:
    from hypergraphs.semirings.sampling.lazy2 import Sample

    # much slower because we have to sample more random variates
    #from hypergraphs.semirings.sampling.lazy import Sample


def extract(xs):
    while isinstance(xs, Sample): xs = xs.d
    if isinstance(xs, list):
        for x in xs:
            yield from extract(x)
    else:
        yield xs


def extract2(xs):
    if isinstance(xs, Sample):
        return extract2(xs.d)
    if isinstance(xs, list):
        r = []
        for x in xs:
            r.append(extract2(x))
        return r
    else:
        return xs


def test_flat():

    n = 5
    w = random_dist(n)**2
    w /= w.sum()

    c = np.zeros(n)
    p = w
    reps = 10_000

    def run():
        Z = Sample.zero
        for k in range(n):
            Z += Sample(w[k], k)
        return Z

    if EAGER:
        def sampler():
            while True:
                yield run().value
    else:
        def sampler():
            yield from run()


#    sample = lazy_sampler()
    sample = iter(sampler())

    for r in range(1, 1+reps):
        _, z = next(sample)
        c[z] += 1
        if r % 10_000 == 0:
            print(f'err({r})=', 0.5*np.abs(p - c/r).sum())

    c /= reps
    print(p)
    print(c)

    compare(p, c)
    #pl.plot(c/reps)
    #pl.plot(p)
    #pl.show()


from hypergraphs.apps.parser2 import parse, load_grammar
def parser(sentence, grammar, w, Weights):
    def binary(sentence,X,Y,Z,i,j,k):
        return Weights(w(X,Y,Z,i,j,k), X)
    def unary(sentence,X,Y,i,k):
        return Weights(w(X,Y,i,k), X)
    def terminal(sentence,W,i):
        return Weights(1.0, W)
    return parse(sentence, grammar, binary, unary, terminal, zero = Weights.zero)[0,len(sentence),'S']


def test_subsets():
    from swor.cps import ConditionalPoissonSampling

    n = 5
    K = 3
    w = random_dist(n)

    cps = ConditionalPoissonSampling(w, K)
    p = {Y: cps.score(Y)/cps.Z for Y in cps.domain()}

    reps = 10_000
    c = {Y: 0 for Y in p}

    if EAGER:
        def sampler():
            while True:
                _, y = subsets(w, K, Sample).value
                yield frozenset(extract(y))

    else:
        def sampler():
            for _, y in subsets(w, K, Sample):
                yield frozenset(extract(y))


    sample = iter(sampler())

    for r in range(1, 1+reps):
        Y = next(sample)
        c[Y] += 1
        if r % 10_000 == 0:
            print(f'err({r})=', 0.5*sum(abs(p[x] - c[x]/r) for x in p))

    for Y in c:
        c[Y] /= reps

    if 1:
        for Y in cps.domain():
            print(f'{cps.score(Y)/cps.Z:.3f}, {c[Y]:.3f} {Y}')
        compare(p, c)#.show()


def test_parse():
    from arsenal.cache import memoize
    from hypergraphs.semirings import LazySort

    w = memoize(lambda *edge: np.exp(np.random.randn()))

    sentence = 'Papa ate the caviar with the spoon .'.split()

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
            p[str(extract2(x.data))] = x.score
            Z += x.score
        return normalize(p)

    p = distribution()

    # TODO: make the parser return a the root rather than the full chart.
    q = {x: 0 for x in p}
    reps = 10_000

    def run():
        return parser(sentence, grammar, w, Sample)

    if EAGER:
        def sampler():
            while True:
                yield run().value

    else:
        def sampler():
            yield from run()


    sample = iter(sampler())
    #sample = iter(lazy_sampler())

    for r in iterview(range(1, 1+reps)):
        _, s = next(sample)
        q[str(s)] += 1

        if r % 1_000 == 0:
            print(f'\nerr({r})=', 0.5*sum(abs(p[x] - q[x]/r) for x in p))

    q = normalize(q)

#    for x in p:
#        print(p[x], q.get(x, 0.0), x)

    compare(p, q)#.show()


def normalize(p):
    Z = sum(p.values())
    q = {}
    for x in p:
        q[x] = p[x]/Z
    return q


if __name__ == '__main__':
    test_flat()
    test_subsets()
    test_parse()
