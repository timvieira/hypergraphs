"""Hypergraph-specific derivation post-processing.

These helpers operate on derivations that bottom out in `hypergraphs.hypergraph.Edge`
instances, so they live here rather than in the (hypergraph-agnostic) `semirings`
package.
"""


def post_process(f, derivation):
    "f: Edge -> str; derivation: list of lists with edges at the leaves."
    from nltk.tree import ImmutableTree as Tree
    from hypergraphs.hypergraph import Edge

    def _post_process(x):
        "Converts nested lists into nicely formatted nltk.Tree's."
        if isinstance(x, Edge): return f(x)
        [a, b] = x
        a = _post_process(a)
        b = _post_process(b)
        if isinstance(b, str): b = (b,)
        if isinstance(a, str):
            return Tree(a, b)
        else:
            return (a, b)    # assume that the parent will label this pair of children

    return _post_process(derivation)


def post_process2(f, derivation):
    "f: Edge -> str; derivation: list of lists with edges at the leaves."
    from hypergraphs.hypergraph import Edge

    def _post_process(x):
        "Converts nested lists into nicely formatted nltk.Tree's."
        if isinstance(x, Edge): return f(x)
        z = tuple(_post_process(y) for y in x)
        if z and isinstance(z[0], str) and isinstance(z[1], tuple):
            assert len(z) == 2
            return (z[0], *z[1])
        return z

    return _post_process(derivation)
