from hypergraphs.hypergraph import Edge
from hypergraphs.apps.parse import parse_forest
from nltk.tree import ImmutableTree


def post_process(x):
    "Converts nested lits into nicely formatted `nltk.Tree`s."
    if isinstance(x, Edge): return x.head[2]
    [a, b] = x
    if isinstance(a, Edge): a = a.head[2]
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
    Z = H.Z()
    for x in H.sorted():
        print(float(x.score/Z), post_process(x.data))


if __name__ == '__main__':
    test_kbest()
