import numpy as np
from collections import defaultdict
from arsenal.iterview import iterview
from hypergraphs.semirings.logval import LogVal
from hypergraphs.apps.parse import parse_forest


def _test_sample_tree(forest, N):
    IO = forest.node_marginals(*forest.sum_product())
    pcfg = forest.to_PCFG()
    _test_sample(pcfg.sample, IO, N)


def _test_pcfg(forest):

    # run inside-outside
    IO = forest.node_marginals(*forest.sum_product())

    pcfg = forest.to_PCFG()

    B, A = pcfg.sum_product()
    for x in B:
        assert np.allclose(float(B[x]), 1), [x, float(B[x])]
    for x in A:
        assert np.allclose(float(IO[x]), float(A[x])), [x, float(IO[x]), float(A[x])]

    print('[test pcfg] ok')


def _test_sample(sample, IO, N):

    # compute marginals
    # TODO: test the probability of the entire tree rather than marginals.
    m = defaultdict(float)
    for _ in iterview(range(N)):
        t = sample()
        for s in t.subtrees():
            x = s.label()
            m[x] += 1.0 / N

    # check marginals
    threshold = 1e-4
    for x in IO:
        (I,K,X,T) = x
        if K-I > 1:
            a = float(IO[x])
            b = m[x]
            if a > threshold or b > threshold:
                print('[%s %s %8s, %s] %7.3f %7.3f' \
                    % (I, K, X, T, a, b))
                assert abs(a - b) < 0.01

    print('[test sample] ok')


def test_sample_tree():
    from hypergraphs.apps.parse import papa_grammar

    forest = parse_forest('Papa ate the caviar with the spoon .'.split(), papa_grammar)
    forest = forest.apply(lambda e: LogVal(ell=e.weight, pos=True))

    _test_pcfg(forest)
    _test_sample_tree(forest, 10000)


if __name__ == '__main__':
    test_sample_tree()
