"""
Segmentations of a sequence.
"""

def segmentation(x, g, Weight, L=None):
    "Segmentations of a sequence, x."
    N = len(x)
    L = N if L is None else L
    V = Weight.chart()
    V[0] = Weight.one
    for i in range(1, N+1):
        for j in range(max(i-L,0), i):
            w = g(x[j:i])
            if w is None: continue
            V[i] += V[j] * Weight.lift(w, x[j:i])
    return V[N]
