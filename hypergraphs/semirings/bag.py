import itertools
from collections import defaultdict
from arsenal import colors
from hypergraphs.semirings import base


class Bag(base.Semiring):

    def __init__(self, bag=None):
        self.bag = defaultdict(int)
        if bag is not None:
            self.bag.update(bag)

    def __add__(self, other):
        new = Bag()
        for k, v in self:
            new.bag[k] += v
        for k, v in other:
            new.bag[k] += v
        return new

    def __sub__(self, other):
        new = Bag()
        for k,v in self:
            new.bag[k] += v
        for k,v in other:
            new.bag[k] -= v
        return new

    def __iter__(self):
        return iter(self.bag.items())

    def __mul__(self, other):
        return Bag({(x, y): xm*ym for x, xm in self for y, ym in other})

    def __repr__(self):
        return 'Bag(%s)' % dict(self.bag)

    @classmethod
    def lift(cls, w, d):
        return Bag({d: w})


Bag.zero = Bag()
Bag.one = Bag({(): 1})
