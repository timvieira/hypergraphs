from hypergraphs.semirings import base


class Bottleneck(base.Semiring):

    def __init__(self, score, d):
        self.score = score
        self.d = d

    def __add__(self, other):
        if self.score >= other.score:
            return self
        else:
            return other

    def __mul__(self, other):
        if self.score <= other.score:
            return self
        else:
            return other

    def __repr__(self):
        return f'Bottleneck({self.score}, {self.d})'


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
