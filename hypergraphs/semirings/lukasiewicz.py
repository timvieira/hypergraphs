from hypergraphs.semirings import base


class Lukasiewicz(base.Semiring):
    """The Łukasiewicz semiring: the closed interval [0,1] with addition given by
    max(a,b) and multiplication given by max(0, a + b - 1) appears in
    multi-valued logic.

    """

    def __init__(self, score, d):
        self.score = score
        self.d = d

    def __add__(self, other):
        return max(self, other)

    def __mul__(self, other):
        return max(0, self.score + other.score - 1, [self, other])

    def __lt__(self, other):
        return self.score < other.score

    def __repr__(self):
        return f'Łukasiewicz({self.score}, {self.d})'

    def multiplicity(self, m):
        if m > 0:
            return self
        else:
            return self.zero


Lukasiewicz.zero = zero = Lukasiewicz(0, None)
Lukasiewicz.one = one = Lukasiewicz(1, ())


if __name__ == '__main__':
    test()
