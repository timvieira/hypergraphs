class CutSets:
    """Set of cut sets

    Implements: Martelli (1976) "A Gaussian Elimination Algorithm for the
    Enumeration of Cut Sets in a Graph"

    """
    def __init__(self, *sets):
        assert all(isinstance(x, (frozenset, set)) for x in sets)
        self.sets = set(min_sets(map(frozenset, sets)))  # project onto minimal set
    def __repr__(self):
        return '{%s}' % (', '.join(repr(set(x) or {}) for x in self.sets))
    def __eq__(self, other):
        return self.sets == other.sets
    def __mul__(self, other):
        return CutSets(*(self.sets | other.sets))
    def __add__(self, other):
        return CutSets(*{
            (x | y)
            for x in self.sets
            for y in other.sets
        })
    def __iter__(self):
        return iter(self.sets)
    @classmethod
    def samples(cls):
        return [
            cls({(2,3)}, {(1,3), (2,4)}),
            cls({(1,3), (2,3)}, {(1,3), (2,4)}),
            cls({(1,3)}),
            cls.zero,
            cls.one,
        ]
    def star(self):
        return self.one #+ self


def min_sets(xs):
    """
    Add r to the collection.
    Returns True if r was subsumed by a more general rule in the program
    Returns False otherwise.
    """
    ys = []
    for x in xs:
        add(ys, x)
    return ys


def add(xs, r):
    # This implementation is pretty inefficient as it is based on linear scan
    rm = []
    for i, s in enumerate(xs):
        # branch r is already subsumed by branch s
        if s < r: return True
        # new branch subsumes existing branch, will be deleted in favor of the
        # more general branch.
        if r < s: rm.append(i)
    for i in reversed(sorted(rm)):
        del xs[i]
    xs.append(r)
    return False


CutSets.zero = CutSets(set())
CutSets.one = CutSets()
