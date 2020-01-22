from nltk import ImmutableTree as Tree

class Enumeration(object):
    """Element of Enumeration semiring.

    Each element is a set of derivations.

    +: union
    x: join/cross product

    See also:

    - `post_process`:

    """

    def __init__(self, x):
        self.x = x

    def __add__(self, other):
        if not other.x:
            return self
        if not self.x:
            return other
        return Enumeration(other.x + self.x)

    def __mul__(self, other):
        if self.x == [None]:   # multiplication by one.
            return other
        if other.x == [None]:  # multiplication by one.
            return self
        return Enumeration([x * y for x in self.x for y in other.x])

    def __repr__(self):
        return 'Enumeration(%s)' % self.x

    @classmethod
    def zero(self):
        return Enumeration([])

    @classmethod
    def one(self):
        return Enumeration([None])


class Fn(object):
    """
    Use in derivation semiring. These are the elements of the sets.

    Multiplication is (partial) functional application.
    """
    def __init__(self, f):
        self.f = f
    def __mul__(self, y):
        z = self.f(y)
        return z if isinstance(z, Tree) else Fn(z)
    def __repr__(self):
        return '`%s`' % self.f
    @classmethod
    def rule(cls,x,y,z):
        "Utility for creating Fn elements."
        def f(yp):
            assert yp == y or yp.label() == y
            def g(zp):
                assert zp == z or zp.label() == z
                return Tree(x, [yp, zp])
            return g
        return cls(f)


def enumerate_derivations(E, root):
    from hypergraphs.hypergraph import Hypergraph

    # Build hypergraph from edge set (no enumeration over derivations required)
    g = Hypergraph()
    g.root = root

    # For computing risk using the second-order expectation semiring we set the
    # edge weights as follows: k_e = (p, p*r, p*s p*r*s). Note: the equivalent
    # computation in the brute-force setting does not do this transformation.
    for e, _ in E.items():
        if len(e) == 3:
            [x,y,z] = e
            ke = Enumeration([Fn.rule(x,y,z)])
            g.edge(ke, x, y, z)
        else:
            [x] = e
            ke = Enumeration([x])
            g.edge(ke, x)

    # Inside algorithm for computing the same stuff as above more efficiently.
    B = g.inside(zero=Enumeration.zero)
    return B[g.root]
