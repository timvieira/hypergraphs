from nltk import ImmutableTree


# TODO: Viterbi is max/+ semiring crossed with a Free semiring for backpointers.
class Viterbi(object):

    def __init__(self, score, d):
        self.score = score
        self.d = d

    def __add__(self, other):
        if self.score >= other.score:
            return Viterbi(self.score, self.d)
        else:
            return Viterbi(other.score, other.d)

    def __mul__(self, other):
        return Viterbi(self.score + other.score, (self, other))

    def derivation(self):
        return _derivation(self)

    def __repr__(self):
        return f'{self.derivation()}'


# XXX: possible duplicate with hypergraph project.
#class Enumeration(object):
#    """Element of Enumeration semiring.
#
#    Each element is a set of derivations.
#
#    +: union
#    x: join/cross product
#
#    See also:
#
#    - `post_process`:
#
#    """
#
#    def __init__(self, x):
#        self.x = x
#
#    def __add__(self, other):
#        if not other.x:
#            return self
#        if not self.x:
#            return other
#        return Enumeration(other.x + self.x)
#
#    def __mul__(self, other):
#        return Enumeration([(x, y) for x in self.x for y in other.x])
#
#    def __repr__(self):
#        return 'Enumeration(%s)' % self.x


def _derivation(x):
    """Post-process `Viterbi` and `Point` derivations into nicely formatted `Tree`
    objects.

    """
    if not isinstance(x.d, (list, tuple)):
        return x.d
    assert len(x.d) == 2
    label = x.d[1].d
    body = x.d[0].d
    if isinstance(body, (list, tuple)):
        return ImmutableTree(label, list(map(_derivation, body)))
    else:
        return ImmutableTree(label, [body])


def post_process(x):
    "Converts elements of `Enumeration` set into nicely formatted `Tree` objects."
    if not isinstance(x, tuple):
        return x
    [body, label] = x
    if isinstance(body, tuple):
        return ImmutableTree(label, list(map(post_process, body)))
    else:
        return ImmutableTree(label, [body])
