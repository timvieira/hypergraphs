"""Matrix-chain multiplication as a hypergraph.

Given matrix dimensions $d_0, \\ldots, d_N$ defining matrices $M_i$ of
shape $d_i \\times d_{i+1}$, build the forest whose derivations are the
parenthesizations of $M_0 M_1 \\cdots M_{N-1}$. Each hyperedge
$(i, j) \\xleftarrow{d_i d_{k+1} d_{j+1}} (i, k)\\,(k+1, j)$ is weighted
by the cost of the outer multiplication when splitting at position $k$;
empty-body edges $(i, i) \\xleftarrow{\\mathbf{1}}$ ground the recursion.

Reference: https://en.wikipedia.org/wiki/Matrix_chain_multiplication
"""

from hypergraphs import Hypergraph


def matrix_chain(dims, W):
    """Build the matrix-chain hypergraph for matrices with the given
    dimensions, weighted in the semiring ``W``.

    ``dims`` is a dimension sequence with $M_i$ having shape
    ``dims[i] x dims[i+1]``. ``W`` is a semiring class exposing
    ``W.one`` and ``W.lift(value, provenance)``. The returned hypergraph
    is rooted at ``(0, N-1)`` where ``N = len(dims) - 1``.
    """
    N = len(dims) - 1
    g = Hypergraph(root=(0, N-1))
    for i in range(N):
        g.edge(W.one, (i, i))
    for span in range(1, N):
        for i in range(N - span):
            j = i + span
            for k in range(i, j):
                cost = dims[i] * dims[k+1] * dims[j+1]
                g.edge(W.lift(cost, (i, j, k)), (i, j), (i, k), (k+1, j))
    return g
