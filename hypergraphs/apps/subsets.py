"""
Subsets of N items of size K.
"""

def subsets(w, K, Weights):
    "Subsets of size K"
    N = len(w)
    E = Weights.chart()
    for n in range(N):
        E[0,n] = Weights.one             # initialization
    for k in range(1, K+1):
        for n in range(N):
            E[k,n+1] += E[k,n]
            E[k,n+1] += E[k-1,n] * Weights.lift(w[n], n)
    return E[K,N]
