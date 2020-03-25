import numpy as np
from hypergraphs.apps.parse import parse_forest
from hypergraphs.semirings.lazysort import BaseCase
from nltk.tree import ImmutableTree


def kbest_parses(_forest):
    forest = _forest.apply(lambda e: BaseCase(e.weight, e.head[2]))
    # run inside-outside
    B = forest.inside()
    for x in B[forest.root]:
        yield x.score, post_process(x.data)


def post_process(x):
    "Converts elements of `Enumeration` set into nicely formatted `Tree` objects."
    if isinstance(x, str): return x
    [a, b] = x
    if isinstance(a, str):
        r = post_process(b)
        if isinstance(r, str): r = [r]
        return ImmutableTree(a, r)
    else:
        return [post_process(a), post_process(b)]


def test_kbest():
    # XXX: add an automated test.
    from hypergraphs.apps.parse import papa_grammar

    H = parse_forest('Papa ate the caviar with the spoon .'.split(), papa_grammar)

    Z = H.inside()[H.root]
    for score, d in kbest_parses(H):
        print(float(score/Z), d)


if __name__ == '__main__':
    test_kbest()