from nltk import ImmutableTree
from hypergraphs.semirings import base


class MaxPlus(base.Semiring):

    def __init__(self, score, d):
        self.score = score
        self.d = d

    def __add__(self, other):
        if other is MaxPlus.zero: return self
        if self is MaxPlus.zero: return other
        if self.score >= other.score:
            return self
        else:
            return other

    def __mul__(self, other):
        if other is MaxPlus.one: return self
        if self is MaxPlus.one: return other
        return MaxPlus(self.score + other.score, (self, other))

    def __lt__(self, other):
        return self.score < other.score

    def derivation(self):
        return _derivation(self)

    def __repr__(self):
        return f'MaxPlus({self.score}, {self.d})'


MaxPlus.zero = MaxPlus(float('-inf'), None)
MaxPlus.one = MaxPlus(0.0, ())


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
    "Converts list of lists set into nicely formatted `Tree` objects."
    if not isinstance(x, tuple):
        return x
    [body, label] = x
    if isinstance(body, tuple):
        return ImmutableTree(label, list(map(post_process, body)))
    else:
        return ImmutableTree(label, [body])
