from nltk import ImmutableTree


def derivation(x):
    """Post-process `Viterbi` and `Point` derivations into nicely formatted `Tree`
    objects.

    """
    if not isinstance(x.d, (list, tuple)):
        return x.d
    assert len(x.d) == 2
    label = x.d[1].d
    body = x.d[0].d
    if isinstance(body, (list, tuple)):
        return ImmutableTree(label, list(map(derivation, body)))
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
