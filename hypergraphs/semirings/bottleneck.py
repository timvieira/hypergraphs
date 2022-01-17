from hypergraphs.semirings import base

# The Łukasiewicz semiring: the closed interval [0,1] with addition given by
# max(a,b) and multiplication given by max(0, a + b - 1) appears in multi-valued
# logic.

class Bottleneck(base.Semiring):

    def __init__(self, score, d):
        self.score = score
        self.d = d

    def __add__(self, other):
        return max(self, other)

    def __mul__(self, other):
        return min(self, other)

    def __lt__(self, other):
        return self.score < other.score

    def __repr__(self):
        return f'Bottleneck({self.score}, {self.d})'

    def multiplicity(self, m):
        if m > 0:
            return self
        else:
            return self.zero


inf = float('inf')
zero = Bottleneck(-inf, None)
one = Bottleneck(inf, ())

Bottleneck.zero = zero
Bottleneck.one = one


def test():
    a = Bottleneck(1, 'a')
    b = Bottleneck(2, 'b')
    c = Bottleneck(3, 'c')
    d = Bottleneck(4, 'd')

    assert (a * b + b * c + d * c) == c
    assert (a + b) == b
    assert (a * b) == a
    assert a * one == a
    assert a * zero == zero
    assert a + zero == a
    assert b + one == one
    print('ok')


if __name__ == '__main__':
    test()
