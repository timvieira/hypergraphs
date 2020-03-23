import numpy as np
from numpy.random import uniform
from hypergraphs.hypergraph import Hypergraph
from hypergraphs.apps.parse import parse_forest

from algebra.number.lazysort import sorted_product
from arsenal.iterextras import merge_sorted
from nltk.tree import ImmutableTree


class LazySort:
    def __add__(self, other):
        if self.is_zero(): return other
        if other.is_zero(): return self
        return Sum(self, other)
    def __radd__(self, other): return other + self
    def __mul__(self, other):
        if self.is_zero(): return zero
        if other.is_zero(): return zero
        return Prod(self, other)
    def is_zero(self):
        return self is zero


# Notice that in this semiring multiplication is neither associative, nor
# commutative.  This is why we get out a derivation tree (with parentheses).
class BaseCase(LazySort):
    def __init__(self, score, data):
        assert isinstance(score, float)
        self.score = score
        self.data = data
    def __mul__(self, other):
        if self.is_zero(): return zero
        if other.is_zero(): return zero
        if isinstance(other, BaseCase):
            return BaseCase(self.score + other.score, [self.data, other.data])
        else:
            return super().__mul__(other)
    def __lt__(self, other):
        return self.score > other.score   # Warning: this is backwards!
    def __iter__(self):
        yield self
    def __repr__(self):
        return repr((self.score, self.data))


zero = BaseCase(np.inf, None)

class Sum(LazySort):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __iter__(self):
        yield from merge_sorted(self.a, self.b)


class Prod(LazySort):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __iter__(self):
        yield from sorted_product(np.product, self.a, self.b)


def kbest_parses(example, grammar):
    _forest = parse_forest(example, grammar)

    # TODO: can we just overwrite the edge weights?
    forest = Hypergraph()
    forest.root = _forest.root
    for e in _forest.edges:
        c = BaseCase(e.weight, e.head[2])
        forest.edge(c, e.head, *e.body)

    # run inside-outside
    B = forest.inside(zero=lambda:zero)
    Z = B[forest.root]

    for x in Z:
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
    for score, d in kbest_parses('Papa ate the caviar with the spoon .'.split(), papa_grammar):
        print(np.exp(score), d)


if __name__ == '__main__':
    test_kbest()
