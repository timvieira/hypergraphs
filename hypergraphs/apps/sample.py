import numpy as np
from collections import defaultdict
from arsenal.iterview import iterview
from numpy.random import uniform
from nltk.tree import ImmutableTree as Tree
from hypergraphs.logval import LogVal
from hypergraphs.hypergraph import Hypergraph
from hypergraphs.apps.parse import parse_forest


# XXX: Does this sampling routine work for arbitrary hypergraphs? (I think it does.)
def sample(forest, B, v=None):
    """ Sample from parse forest. """
    if v is None:
        v = forest.root
    edges = forest.incoming[v]
    if not edges:
        # base case (leaf), nothing to sample
        return v
    # sample incoming edge, p(e|head) \propto edge.weight * (\prod_{b in e.body} beta[b])
    Z = LogVal.Zero()
    cs = []
    for e in edges:
        p = e.weight
        for y in e.body:
            p *= B[y]
        Z += p
        cs.append(Z.to_real())
    # sample one of the incoming edges
    i = np.array(cs).searchsorted(uniform(0, cs[-1]))
    e = edges[i]
    return Tree(v, [sample(forest, B, y) for y in e.body])


def sum_product(forest):
    "Run inside-outside on forest (logprob)."
    B = forest.inside(zero=LogVal.Zero)
    A = forest.outside(B, zero=LogVal.Zero, one=LogVal.One)
    return B, A


def _test_sample_tree(example, grammar, N):
#    gold = {(X,I,K) for (X,I,K) in example.gold_items if (I,K) in example.nodes}
    print()
    _forest = parse_forest(example, grammar)
    # apply temperature to grammar rules
    forest = Hypergraph()
    forest.root = _forest.root
    for e in _forest.edges:
        c = LogVal.Zero()
        c.logeq(e.weight)
        forest.edge(c, e.head, *e.body)
    # run inside-outside
    B, A = sum_product(forest)
    Z = B[forest.root]
    # compute marginals and recall from samples
#    sample_recall = 0.0
    m = defaultdict(float)
    for _ in iterview(range(N)):
        t = sample(forest, B)
        for s in t.subtrees():
            x = s.label()
            m[x] += 1.0 / N
#            xx = rename(grammar, x)
#            sample_recall += (xx in gold) * 1.0 / N
    # convert node names and marginalize-out time index
    IO = defaultdict(float)
    for x in forest.incoming:
        IO[x] += (B[x] * A[x] / Z).to_real()
    # check marginals
    threshold = 1e-4
    for x in IO:
        (I,K,X,T) = x
        if K-I > 1:
            a = IO[x]
            b = m[x]
            if a > threshold or b > threshold:
                print('[%s %s %8s, %s] %7.3f %7.3f' \
                    % (I, K, X, T, a, b))
                assert abs(a - b) < 0.05
#    print 'expect recall:', sum(IO[X,I,K] for (X,I,K) in gold) / len(gold)
#    print 'sample recall:', sample_recall / len(gold)


def test_sample_tree():
    from hypergraphs.apps.parse import papa_grammar
    _test_sample_tree('Papa ate the caviar with the spoon .'.split(), papa_grammar, 1000)


if __name__ == '__main__':
    test_sample_tree()
