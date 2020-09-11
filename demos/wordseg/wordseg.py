"""
Top-k segementations of unintentionally funny URLs.
"""
import numpy as np
from collections import defaultdict
from hypergraphs.semirings import LazySort
from arsenal import colors
from arsenal.iterextras import take


def segmentation(x, g, L=None):
    N = len(x)
    L = N if L is None else L
    V = np.full(N+1, LazySort.zero())

    V[0] = LazySort.one()
    for i in range(1, N+1):
        for j in range(max(i-L,0), i):
            w = g(x[j:i])
            if w is None: continue
            V[i] += V[j] * LazySort(w, x[j:i])

    return V[N]


def test():

    from path import Path
    freq = defaultdict(lambda : 0.0)
    for line in open(Path(__file__).dirname() / 'unigrams.txt'):
        w, x = line.lower().strip().split()
        freq[w] = float(x)
    z = sum(freq.values())
    freq = {w: freq[w]/z for w in freq}

    def score(w):
        return freq.get(w)

    examples = [
        'penisland',
        'powergenitalia',
        'bobwehadababyitsaboy',
        'speedofart',
        'expertsexchange',
        'whorepresents',
    ]

    for x in examples:
        print()
        print(colors.light.yellow % f'{x}')
        for y in take(5, segmentation(x, score)):
            print(y)


if __name__ == '__main__':
    test()
