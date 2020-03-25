import numpy as np
from arsenal.iterextras import sorted_union, sorted_product


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
    @classmethod
    def zero(cls):
        return BaseCase(np.inf, None)


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


zero = LazySort.zero()

class Sum(LazySort):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __iter__(self):
        yield from sorted_union(self.a, self.b)


class Prod(LazySort):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __iter__(self):
        yield from sorted_product(np.product, self.a, self.b)
