from itertools import chain
from arsenal.iterextras import buf_iter

class Enumeration(object):
    """
    Enumeration semiring.

    Each element is a lazy set of derivations.
    +: lazy union
    x: lazy cross product
    """

    def __init__(self, x):
        self.x = buf_iter(x)

    def __add__(self, other):
        if not other.x: return self
        if not self.x:  return other
        return Enumeration(chain(other.x, self.x))

    def __mul__(self, other):
        # multiplication by one.
        if self.x is one:  return other
        if other.x is one: return self
        return Enumeration(((x, y) for x in self for y in other))

    def __iter__(self):
        return iter(self.x)

    def __repr__(self):
        return f'Enumeration({list(self.x)})'

    @classmethod
    def zero(cls):
        return zero

    @classmethod
    def one(cls):
        return one


one = Enumeration([None])
zero = Enumeration([])
