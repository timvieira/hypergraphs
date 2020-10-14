import numpy as np
from nltk.tree import ImmutableTree as Tree
from arsenal.maths import sample

from hypergraphs.hypergraph import Hypergraph


class WCFG(Hypergraph):

    def sum_product(self):
        "Run inside-outside on forest (logprob)."
        B = self.inside()
        A = self.outside(B)
        return B, A

    def node_marginals(self, B, A):
        Z = self.Z()
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
        B = self.inside()
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

    def sample(self):
        "Sample from parse forest."
        return PDA(self).run()


class PDA:
    def __init__(self, g):
        assert isinstance(g, PCFG)
        self.g = g
        self.total = g.kind.one
        self.closed = []
        self.stack = []

    def run(self):
        closed = self.closed
        stack = self.stack
        stack.append(self.sample(self.g.root))
        while stack:
            v = stack[-1]

            b = None
            if v.rule and v.dot < len(v.rule.body):
                assert v.rule is not None and v.dot is not None
                b = v.rule.body[v.dot]
                v.dot += 1
                b = self.sample(b)

            if b is None:
                stack.pop(-1)
                closed.append(v)
            else:
                stack.append(b)
        return self.derivation()

    def sample(self, v):
        "Sample an edge (dotted rule)."
        assert isinstance(v, tuple)

        edges = self.g.incoming[v]
        # base case (leaf), nothing to sample
        if not edges: return
        # sample incoming edge, p(e|head) \propto edge.weight * (\prod_{b in e.body} beta[b])
        ws = [e.weight for e in edges]
        ps = [float(e.weight) for e in edges]
        # sample one of the incoming edges
        i = sample(ps)
        e = edges[i]
        self.total *= ws[i]

        return DottedRule(e)

    def derivation(self):
        S = Hypergraph(self.g.root)
        for e in self.closed:
            e = e.rule
            S.edge(e.weight, e.head, *e.body)
        return S


class DottedRule:
    def __init__(self, rule):
        self.rule = rule
        self.dot = 0

    def __repr__(self):
        return f'DottedRule({self.dot}, {self.rule})'

    def expand_next(self):
        if self.rule and self.dot < len(self.rule.body):
            assert self.rule is not None and self.dot is not None
            b = self.rule.body[self.dot]
            self.dot += 1
            return new(b)
