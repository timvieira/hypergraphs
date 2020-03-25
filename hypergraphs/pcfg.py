import numpy as np
from nltk.tree import ImmutableTree as Tree
from arsenal.maths import sample

from hypergraphs.hypergraph import Hypergraph
from hypergraphs.semirings.logval import LogVal


class WCFG(Hypergraph):

    def sum_product(self):
        "Run inside-outside on forest (logprob)."
        B = self.inside(zero=LogVal.zero)
        A = self.outside(B, zero=LogVal.zero, one=LogVal.one)
        return B, A

    def node_marginals(self, B, A):
        Z = B[self.root]
        return {x: B[x] * A[x] / Z for x in A}

    def edge_marginals(self, B, A):
        M = {}
        for e in self.edges:
            w = A[e.head] * e.weight
            for y in e.body:
                w *= B[y]
            M[e] = w
        return M

    def to_PCFG(self):
        B = self.inside(zero=LogVal.zero)
        P = PCFG()
        P.root = self.root
        for _, es in self.incoming.items():   # edges grouped by head node.
            ws = []
            for e in es:
                w = e.weight
                for y in e.body:
                    w *= B[y]
                ws.append(w)
            Z = np.sum(ws)
            for w, e in zip(ws, es):
                P.edge(w/Z, e.head, *e.body)
        return P


class PCFG(WCFG):
    def sample(self, v=None):
        "Sample from parse forest."
        if v is None: v = self.root
        edges = self.incoming[v]
        # base case (leaf), nothing to sample
        if not edges: return v
        # sample incoming edge, p(e|head) \propto edge.weight * (\prod_{b in e.body} beta[b])
        ps = [float(e.weight) for e in edges]
        # sample one of the incoming edges
        i = sample(ps)
        e = edges[i]
        return Tree(v, [self.sample(y) for y in e.body])
