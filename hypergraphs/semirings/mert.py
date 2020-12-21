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
    def draw(self, label_fmt=None):
        "Visualize points with interactive scatter plot browser."
        if not self.points:
            print('[warn] ConvexHull is empty.')
            return

        import scipy.spatial
        points = np.array([(p.x, p.y) for p in self.points])
        hull = scipy.spatial.ConvexHull(points)
        for simplex in hull.simplices:
            pl.plot(points[simplex, 0], points[simplex, 1], 'k-', zorder=-1, alpha=0.5, lw=.5)

        for p in self:
            pl.scatter(p.x, p.y, c='r', alpha=0.5, zorder=-1)

        pl.box(False)
        pl.xticks([p.x for p in self], rotation='vertical')
        pl.yticks([p.y for p in self])
        for p in self:
            pl.text(x=p.x, y=p.y, s=str(p.d) if label_fmt is None else label_fmt(p))


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
