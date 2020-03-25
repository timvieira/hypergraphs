"""
MERT semiring
"""
import numpy as np
import pylab as pl
from scipy.spatial.qhull import Delaunay

from pandas import DataFrame
from hypergraphs.semirings.viterbi import _derivation, post_process
#from hypergraphs.enumeration import Enumeration, Fn


def conv(points):
    "Indices of the convex hull."
    _points = points
    points = np.array([(x.m, x.b) for x in points])
    if len(points) <= 2:
        hul = range(len(points))
    else:
        tri = Delaunay(points)
        hul = list({v for x in tri.convex_hull for v in x})
    return list(np.array(_points)[hul])


class Point(object):
    """Two-dimensional point with backpointers so that we can reconstruct the
    derivation.

    """

    def __init__(self, m, b, d):
        self.m = m
        self.b = b
        self.d = d

    def __repr__(self):
        t = self.derivation()
        d = t._pformat_flat(nodesep='', parens='()', quotes=False)
        return 'Point(%s, %s, %s)' % (self.m, self.b, d)

    def derivation(self):
        return _derivation(self)


class Elem(object):
    """Convex hull semiring (in two-dimensions).

    Each element of this semiring is a convex hull of `Points`.

    Based closely on Chris Dyer's 2013 arxiv paper
    (http://arxiv.org/pdf/1307.3675.pdf)

    Coded for clarity, not efficiency.

    """
    def __init__(self, points):
        self.points = conv(points)
    def __add__(self, other):
        assert isinstance(other, Elem)
        return Elem(list(self.points) + list(other.points))
    def __mul__(self, other):
        # http://en.wikipedia.org/wiki/Minkowski_addition
        assert isinstance(other, Elem)
        return Elem([Point(a.m + b.m, a.b + b.b, (a, b)) for a in self.points for b in other.points])
    def draw(self):
        "Visualize points with interactive scatter plot browser."
        if not self.points:
            print('Elem is empty.')
            return
        df = DataFrame([(x.m, x.b, x.derivation()) for x in self.points], columns=['m','b','d'])
        # Keep a reference to PointBrowser to keep things for breaking do to GC.
        #from arsenal.viz.interact import PointBrowser
        #global br; br = PointBrowser(df, xcol='m', ycol='b')
        pl.scatter(df.m, df.b)
        pl.show()
