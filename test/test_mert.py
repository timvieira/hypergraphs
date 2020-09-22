"""MERT semiring tests
===================

- This module uses an imperative hypergraph traversal strategy (parser2) rather
  than creating a hypergraph data structure (parser).

TODO: Used an edge with features class.

"""
import numpy as np
import pylab as pl
from hypergraphs import Edge
from hypergraphs.semirings import LazySort, ConvexHull, Point, post_process
from hypergraphs.apps.parser2 import parse, load_grammar


def semiring_enumeration(sentence, rhs):
    def binary(_,X,Y,Z,I,J,K): return LazySort(1, X) #Edge(1, (X,I,K), [(Y,I,J), (Z,J,K)]))
    def unary(_,X,Y,I,K):      return LazySort(1, X) #Edge(1, (X,I,K), [(Y,I,K)]))
    def terminal(_,W,I):       return LazySort(1, W) #Edge(1, (W,I,I+1), []))
    c = parse(sentence, rhs, binary, unary, terminal, LazySort.zero)
    return c[0,len(sentence),'S']


def semiring_linesearch(sentence, rhs, weights, step, direction, binary_features, unary_features):
    from hypergraphs.semirings.maxplus import MaxPlus

    def binary(sentence,X,Y,Z,i,j,k):
        fs = binary_features(sentence,X,Y,Z,i,j,k)
        return MaxPlus(weights[fs].sum() + step*direction[fs].sum(), X)

    def unary(sentence,X,Y,i,k):
        fs = unary_features(sentence,X,Y,i,k)
        return MaxPlus(weights[fs].sum() + step*direction[fs].sum(), X)

    def terminal(sentence,W,i):
        return MaxPlus(0, W)     # semiring one

    c = parse(sentence, rhs, binary, unary, terminal, MaxPlus.zero)
    return c[0,len(sentence),'S']


def semiring_mert(sentence, rhs, w, d, binary_features, unary_features):

    def binary(sentence,X,Y,Z,i,j,k):
        fs = binary_features(sentence,X,Y,Z,i,j,k)
        return ConvexHull([Point(w[fs].sum(), -d[fs].sum(), X)])

    def unary(sentence,X,Y,i,k):
        fs = unary_features(sentence,X,Y,i,k)
        return ConvexHull([Point(w[fs].sum(), -d[fs].sum(), X)])

    def terminal(sentence,W,i):
        # semiring one with terminal symbol annotation
        return ConvexHull([Point(0, 0, W)])

    zero = ConvexHull([])

    c = parse(sentence, rhs, binary, unary, terminal, zero)
    return c[0,len(sentence),'S']


def main():
    from arsenal.integerizer import FeatureHashing
    from arsenal.maths import spherical

    bits = 8
    D = 2**bits

    alphabet = FeatureHashing(lambda x: abs(hash(x)), bits)
    weights = spherical(D)
    direction = spherical(D)

    #sentence = 'Papa ate the caviar with the spoon in the park .'.split()
    sentence = 'Papa ate the caviar with the spoon .'.split()

    if 0:
        grammar = """
        S       S .
        S       NP VP
        NP      D N
        NP      NP PP
        VP      V NP
        VP      VP PP
        PP      P NP
        NP      Papa
        N       caviar
        N       spoon
        N       park
        V       ate
        P       with
        P       in
        D       the
        """

    else:
        grammar = """
        S       X .
        X       X X
        X       Papa
        X       ate
        X       the
        X       caviar
        X       with
        X       spoon
        X       in
        X       park
        """

    rhs = load_grammar(grammar)

    if 1:
        # This code branch enumerates all (exponentially many) valid
        # derivations.
        root = semiring_enumeration(sentence, rhs)
        for d in root:
            print(d)
#            print(post_process(lambda e: e, d))
        assert len(list(root)) == len(set(root))

    def binary_features(_,X,Y,Z,i,j,k):
        return alphabet(['%s -> %s %s [%s,%s,%s]' % (X,Y,Z,i,j,k)])

    def unary_features(_,X,Y,i,k):
        return alphabet(['%s -> %s [%s,%s]' % (X,Y,i,k)])

    root = semiring_mert(sentence, rhs, weights, direction, binary_features, unary_features)

    mert_derivations = [] #set()
    for x in root:
        print(x)
        d = x.derivation()
        mert_derivations.append(d)

    assert len(mert_derivations) == len(set(mert_derivations))
    root.draw()

    # Compare the set of derivations found by the MERT semiring to 'brute force'
    # linesearch. Note: Linesearch might only find a subset of derivations found
    # by MERT if the grid isn't fine enough.
    brute_derivations = set()
    for step in np.linspace(-20,20,1000):
        root = semiring_linesearch(sentence, rhs, weights, step, direction, binary_features, unary_features)
        d = root.derivation()
        brute_derivations.add(d)

    # NOTE: need to take upper hull of mert (so it's currently an over estimate)
    print('mert:', len(mert_derivations))
    print('brute:', len(brute_derivations))
    assert brute_derivations.issubset(mert_derivations)


if __name__ == '__main__':
    main()
    pl.show()
