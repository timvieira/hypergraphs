from nltk import ImmutableTree


class Viterbi(object):

    def __init__(self, score, d):
        self.score = score
        self.d = d

    def __add__(self, other):
        if other is zero: return self
        if self is zero: return other
        if self.score >= other.score:
            return self
        else:
            return other

    def __mul__(self, other):
        if other is one: return self
        if self is one: return other
        return Viterbi(self.score + other.score, (self, other))

    def derivation(self):
        return _derivation(self)

    def __repr__(self):
        return f'Viterbi({self.score}, {self.d})'

    @classmethod
    def zero(cls):
        return zero

    @classmethod
    def one(cls):
        return one


ninf = float('-inf')
zero = Viterbi(ninf, None)
one = Viterbi(0.0, ())


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
