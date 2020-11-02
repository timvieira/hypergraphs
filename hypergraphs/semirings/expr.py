"""
New prototype: rather than thinking about hypergraphs just think about
sum-product structures.

Picking a semiring corresponds to "how to interpret the expression" -- i.e.,
"what do you want plus and times to mean?"

The compact expression given be a program can be flattened out (as in
disjunctive normal form) into a 'brute force expression'.  The computation is
"correct" of the operations are invariant to that flattening and the flattened
expression is what you want.  Dynamic programming is nothing more than taking
big expressions and factoring them into smaller expressions.

"""
import numpy as np
from arsenal.iterextras import sorted_union, sorted_product
from hypergraphs.semirings import base


class Expr(base.Semiring):
    def __init__(self, *args):
        self.args = args
        assert isinstance(args, tuple)
    def __lt__(self, other):
        if isinstance(other, Expr):
            return self.args < other.args
        else:
            car = self.args[0] if len(self.args) > 1 else None
            return car < other
    def __add__(self, other):
        if self is zero: return other
        if other is zero: return self
        return Sum(self, other)
    def __mul__(self, other):
        if self is one: return other
        if other is one: return self
        if self is zero: return zero
        if other is zero: return zero
        return Prod(self, other)
    def star(self):
        return Star(self)
    @staticmethod
    def lift(w, d):
        return Expr(w, d)
    def __repr__(self):
        return f'{self.__class__.__name__}({", ".join(map(repr, self.args))})'


Expr.zero = zero = Expr()
Expr.one = one = Expr()


class Sum(Expr):
    def __repr__(self):
        y,z = self.args
        return f'({y} + {z})'


class Prod(Expr):
    def __repr__(self):
        y,z = self.args
        return f'({y} * {z})'


class Star(Expr):
    def __repr__(self):
        [y] = self.args
        return f'star({y})'


def lazysort(x):
    if isinstance(x, Sum):
        y, z = x.args
        yield from sorted_union(lazysort(y), lazysort(z))
    elif isinstance(x, Prod):
        y, z = x.args
        yield from sorted_product(np.product, lazysort(y), lazysort(z))
    elif isinstance(x, Star):
        [y] = x.args
        v = one
        while True:
            yield from lazysort(v)
            v *= y
    elif isinstance(x, Expr):
        yield x
    else:
        assert False


def sample(x):
    "Sample from expr x wrt weighting function w."
    if isinstance(x, Sum):
        y,z = x.args
        if np.random.uniform(0,1) * weight(x) <= weight(y):
            return sample(y)
        else:
            return sample(z)
    elif isinstance(x, Prod):
        y,z = x.args
        return sample(y) * sample(z)
    elif isinstance(x, Star):
        # sample a number of repetitions for a geometric distribution
        zs = one
        [y] = x.args
        while True:
            if np.random.uniform() <= weight(y):   # XXX: Need to normalize this.
                zs = zs*sample(y)
            else:
                return zs
    elif isinstance(x, Expr):
        return x
    else:
        assert False


from arsenal.cache import memoize
@memoize
def weight(x):
    "Sample from expr x wrt weighting function w."
    if isinstance(x, Sum):
        y,z = x.args
        return weight(y) + weight(z)
    elif isinstance(x, Prod):
        y,z = x.args
        return weight(y) * weight(z)
    elif isinstance(x, Star):
        [y] = x.args
        return 1/(1-weight(y))
    elif isinstance(x, Expr):
        # Weights must be specified as base cases.  By convention they should be
        # the first element of the expression's args.
        return x.args[0]
    else:
        assert False


@memoize
def maxtimes(x):
    "Sample from expr x wrt weighting function w."
    if isinstance(x, Sum):
        y,z = x.args
        yy = maxtimes(y)
        zz = maxtimes(z)
        if weight(yy) > weight(zz):
            return yy
        else:
            return zz
    elif isinstance(x, Prod):
        y,z = x.args
        return maxtimes(y) * maxtimes(z)
    elif isinstance(x, Star):
        [y] = x.args
        return maxtimes(y)
    elif isinstance(x, Expr):
        # Weights must be specified as base cases.  By convention, they should
        # be the first element of the expression's args.
        return x
    else:
        assert False


from collections import defaultdict

def backprop(expr):
    """
    Transforms a sum-product graph into another that corresponds to the
    adjoint.
    """

    def visit(Z):
        v = adj[Z]
        if isinstance(Z, Sum):
            X,Y = Z.args
            adj[X] += v
            adj[Y] += v
        elif isinstance(Z, Prod):
            X,Y = Z.args
            adj[X] += v * Y
            adj[Y] += X * v

    adj = defaultdict(lambda: zero)
    adj[expr] = one

    for x in reversed(list(toposort(expr))):
        visit(x)

    return adj


def toposort(root):
    visited = set()

    def t(v):
        if v not in visited:
            visited.add(v)
            if isinstance(v, (Sum, Prod)):
                for y in v.args:
                    yield from t(y)
            yield v

    yield from t(root)


def test():
    c = Expr(3, 'c')
    b = Expr(2, 'b')
    a = Expr(1, 'a')
    d = Expr(2, 'd')
    e = Expr(2, 'e')

    root = a * (c + b + d) * e

    for s in lazysort(root):
        print('>>>', s)

    w = weight(root)
    print(w)

    w = maxtimes(root)
    print(w)

    for _ in range(15):
        s = sample(root)
        print('>>>', s)

    from pprint import pprint
    adj = backprop(root)
    pprint(dict(adj))

    print()
    print(adj[a])


if __name__ == '__main__':
    test()
