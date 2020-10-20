"""
MERT semiring
"""
import numpy as np
import pylab as pl
from scipy.spatial.qhull import Delaunay

from pandas import DataFrame
from hypergraphs.semirings.util import derivation

# TODO: Optimization: Use the LazySort semiring to iterate over points in sorted
# order.  Essentially, the convex hull semiring is just a pruned version of the
# LazySort semiring applied to pairs of numbers. (I believe this can be used to
# amortize the cost of the convex hull operation.  Additionally, the lazy sort
# inherits the same additional operation, but this time it is sorted.)
class ConvexHull:
    """Convex hull semiring (in two-dimensions).

    Each element of this semiring is a convex hull of `Points`.

    Based closely on Chris Dyer's 2013 arxiv paper
    (http://arxiv.org/pdf/1307.3675.pdf)

    Coded for clarity, not efficiency.

    """
    def __init__(self, points):
        self.points = conv(points)
    def __iter__(self):
        return iter(self.points)
    def __add__(self, other):
        if self is zero: return other
        if other is zero: return self
        assert isinstance(other, ConvexHull)
        return ConvexHull(list(self) + list(other))
    def __mul__(self, other):
        if other is one: return self
        if self is one: return other
        if other is zero: return zero
        if self is zero: return zero
        # http://en.wikipedia.org/wiki/Minkowski_addition
        assert isinstance(other, ConvexHull)
        return ConvexHull([Point(a.x + b.x,
                                 a.y + b.y,
                                 (a, b))
                           for a in self
                           for b in other])
    def draw(self):
        "Visualize points with interactive scatter plot browser."
        if not self.points:
            print('[warn] ConvexHull is empty.')
            return
        df = DataFrame([(p.x, p.y, derivation(p)) for p in self],
                       columns=['x','y','d'])
        # Keep a reference to PointBrowser to keep things for breaking do to GC.
        #from arsenal.viz.interact import PointBrowser
        #global br; br = PointBrowser(df, xcol='m', ycol='b')
        pl.scatter(df.x, df.y)
        pl.show()



def conv(points):
    "Indices of the convex hull."
    if len(points) <= 2:
        return points
    else:
        tri = Delaunay(np.array([(x.x, x.y) for x in points]))
        hul = list({v for x in tri.convex_hull for v in x})
        return [points[i] for i in hul]


class Point:
    """
    Two-dimensional point with backpointers so that we can reconstruct the
    derivation.
    """

    def __init__(self, x, y, d):
        self.x = x
        self.y = y
        self.d = d

    def __repr__(self):
        t = derivation(self)
        d = t._pformat_flat(nodesep='', parens='()', quotes=False)
        return f'Point({self.x}, {self.y}, {d})'


zero = ConvexHull([])
one = ConvexHull([Point(0,0,None)])

ConvexHull.zero = zero
ConvexHull.one = one
