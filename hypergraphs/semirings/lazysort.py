import numpy as np
from arsenal.iterextras import sorted_union, sorted_product
from hypergraphs.semirings import base

# TODO: create a LazySort builder which is parametric in the underlying ops,
# just like expectation semiring.  This will reuse code for max-sum, min-sum,
# sum-prod, and even lexicographic semirings.

class _LazySort(base.Semiring):
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
        return self == zero
    def star(self):
        return Star(self)
    def __abs__(self):
        return 0 #abs(self.score)
    @classmethod
    def multiplicity(cls, v, m):
        if m == 0:
            return cls.zero
        else:
            assert m > 0, m
            return v


# Notice that in this multiplication is neither associative, nor commutative.
# This is why we get out a derivation tree (with parentheses).
class LazySort(_LazySort):
    def __init__(self, score, data):
        #assert isinstance(score, (int,float)), score
        self.score = score
        self.data = data
    def __mul__(self, other):
        if self is one: return other
        if other is one: return self
        if self.is_zero(): return zero
        if other.is_zero(): return zero
        if isinstance(other, LazySort):
            return LazySort(self.score * other.score, [self.data, other.data])
        else:
            return super().__mul__(other)
    def __lt__(self, other):
        return other.score < self.score    # Warning: this is backwards!
    def __iter__(self):
        yield self
    def __repr__(self):
        return repr((self.score, self.data))
    def flat_data(self):
        return tuple(sorted(flatten(self.data)))


class Sum(_LazySort):
    def __init__(self, a, b):
        self.a = a
        self.b = b
        assert isinstance(a, _LazySort) and isinstance(b, _LazySort), [a,b]
    def __iter__(self):
        yield from sorted_union(self.a, self.b)
    def __repr__(self):
#        return f'({self.a} + {self.b})'
        return f'sum(...)'


class Prod(_LazySort):
    def __init__(self, a, b):
        self.a = a
        self.b = b
        assert isinstance(a, _LazySort) and isinstance(b, _LazySort), [a,b]
    def __iter__(self):
        yield from sorted_product(np.product, self.a, self.b)
    def __repr__(self):
        return f'({self.a} * {self.b})'


class Star(_LazySort):
    def __init__(self, a):
        self.a = a
        assert isinstance(a, _LazySort)
    def __iter__(self):
        v = one
        while True:
            yield from v
            v *= self.a
    def __repr__(self):
        return f'star({self.a})'


zero = LazySort(0.0, None)
one = LazySort(1.0, ())

LazySort.zero = zero
LazySort.one = one


def post_process(f, derivation):
    "f: Edge -> str; derivation: list of lists with edges at the leaves."
    from nltk.tree import  ImmutableTree as Tree
    from hypergraphs.hypergraph import Edge

    def _post_process(x):
        "Converts nested lists into nicely formatted `nltk.Tree`s."
        if isinstance(x, Edge): return f(x)
        [a, b] = x
        a = _post_process(a)
        b = _post_process(b)
        if isinstance(b, str): b = (b,)
        if isinstance(a, str):
            return Tree(a, b)
        else:
            return (a, b)     # assume that the parent will label this pair of children

    return _post_process(derivation)



def post_process2(f, derivation):
    "f: Edge -> str; derivation: list of lists with edges at the leaves."
    from hypergraphs.hypergraph import Edge

    def _post_process(x):
        "Converts nested lits into nicely formatted `nltk.Tree`s."
        if isinstance(x, Edge): return f(x)
        z = tuple(_post_process(y) for y in x)
        if z and isinstance(z[0], str) and isinstance(z[1], tuple):
            assert len(z) == 2
            return (z[0], *z[1])
        return z

    return _post_process(derivation)


def flatten(S):
    if not isinstance(S, list):
        return [S]
    else:
        tmp = []
        for x in S:
            tmp.extend(flatten(x))
        return tmp
