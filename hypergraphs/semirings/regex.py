from hypergraphs.semirings import base
from arsenal.iterextras import merge_roundrobin, fair_product

from arsenal import colors
#COLOR = '%s'
COLOR = colors.dark.white


class Regex(base.Semiring):
    """
    Regular expressions are compact representation of (possible infinite) sets
    of strings over an alphabet of symbols. I like to think of regular
    expressions as an efficient way to represent the enumeration semiring.
    """

    def expand(self):   # won't terminate with star.
        x = NULL
        for y in self:
            x += y
        return x

    def trunc(self, K):
        x = NULL
        for k, y in enumerate(self):
            x += y
            if k >= K: break
        return x

    def star(self):
        if self is NULL: return EPSILON
        return Star(self)

    def __iter__(self):
        raise NotImplementedError()

    def __add__(self, other):
        if other is NULL: return self
        if self is NULL: return other
        return Disjunction(self, other)

    def __mul__(self, other):
        # multiplication by zero
        if self is NULL or other is NULL: return NULL
        # multiplication by one.
        if self is EPSILON:  return other
        if other is EPSILON: return self
        return Concat(self, other)

    def __round__(self, _):
        return self

    @classmethod
    def _lift(self, x):
        return Symbol(x)


class Disjunction(Regex):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f'{self.x} + {self.y}'
    def __hash__(self):
        return hash((self.x, self.y))
    def __eq__(self, other):
        return self is other or isinstance(other, Disjunction) and self.x == other.x and self.y == other.y
    def __iter__(self):
        yield from merge_roundrobin(self.x, self.y)


class Star(Regex):
    def __init__(self, x):
        assert isinstance(x, Regex)
        self.x = x
    def __repr__(self):
        return f'({self.x})*'
    def __hash__(self):
        return hash(self.x)
    def __eq__(self, other):
        return self is other or isinstance(other, Star) and self.x == other.x
    def __iter__(self):
        p = EPSILON
        while True:
            yield from p
            p = p * self.x


class Concat(Regex):
    def __init__(self, x, y):
        assert isinstance(x, Regex) and isinstance(y, Regex)
        self.x = x
        self.y = y
    def __repr__(self):
        x = self.x; y = self.y
        if isinstance(x, Disjunction): x = f'({x})'
        if isinstance(y, Disjunction): y = f'({y})'
        return f'{x}⋅{y}'
    def __iter__(self):
        for x,y in fair_product(self.x, self.y):
            yield x * y
    def __lt__(self, other):
        if isinstance(other, Concat):
            if self.x != other.x:
                return self.x < other.x
            else:
                return self.y < other.y
        return type(self).__name__ < type(other).__name__
    def __hash__(self):
        return hash((self.x, self.y))
    def __eq__(self, other):
        return self is other or isinstance(other, Concat) and self.x == other.x and self.y == other.y


class Symbol(Regex):
    def __init__(self, x):
        assert isinstance(x, str) or x is None
        self.x = x
    def __repr__(self):
        return COLOR % f'{self.x}'
    def __hash__(self):
        return hash(self.x)
    def __eq__(self, other):
        return isinstance(other, Symbol) and self.x == other.x
    def __iter__(self):
        if self == NULL: return
        yield self
    def __lt__(self, other):
        if isinstance(other, Symbol): return self.x < other.x
        return type(self).__name__ < type(other).__name__


Regex.zero = NULL = Symbol(None)
Regex.one = EPSILON = Symbol('ε')


def test():

    assert set(NULL) == set()
    assert set(EPSILON) == {EPSILON}

    ab = ((Symbol('a') + Symbol('b')) * (Symbol('c') + Symbol('d')))
    assert len(set(ab)) == 4

    for i, x in enumerate((Symbol('a').star() + Symbol('b').star())
                          * (Symbol('c').star() + Symbol('d').star())):
        print(x)

        if i > 25:
            break

    print('test: pass')


if __name__ == '__main__':
    test()
