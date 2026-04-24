from hypergraphs.hypergraph import Hypergraph


class _IaddSentinel:
    __slots__ = ()
_IADD_SENTINEL = _IaddSentinel()


class NodeRef:
    """Proxy returned by `HypergraphBuilder.__getitem__`.

    Supports `*` to build edge bodies and `+=` to append edges.
    """
    __slots__ = ('graph', 'key')

    def __init__(self, graph, key):
        self.graph = graph
        self.key = key

    def __mul__(self, other):
        return _Product._build(self, other)

    def __rmul__(self, other):
        return _Product._build(other, self)

    def __iadd__(self, other):
        self.graph._append_edge(self.key, other)
        return _IADD_SENTINEL

    def __repr__(self):
        return f'NodeRef({self.key!r})'


class _Product:
    """Flattened product expression accumulated by `NodeRef.__mul__`."""
    __slots__ = ('factors',)

    def __init__(self, factors):
        self.factors = factors

    @staticmethod
    def _build(a, b):
        fa = a.factors if isinstance(a, _Product) else [a]
        fb = b.factors if isinstance(b, _Product) else [b]
        return _Product(fa + fb)

    def __mul__(self, other):
        return _Product._build(self, other)

    def __rmul__(self, other):
        return _Product._build(other, self)


class HypergraphBuilder(Hypergraph):
    """Hypergraph with operator-overloading sugar for edge construction.

        g = HypergraphBuilder(Float, root=...)
        g[h] = 1.0                       # nullary axiom:   edge(1.0, h)
        g[h] += g[a]                     # unary edge:      edge(one, h, a)
        g[h] += w * g[a] * g[b]          # binary edge:     edge(w,   h, a, b)

    Scalars inside a product are multiplied together (left-to-right) and
    become the edge's weight. `NodeRef` factors become the edge's body, in
    order. If no scalar appears, weight defaults to `kind.one`.
    """

    def __init__(self, kind, root=None):
        assert kind is not None, "HypergraphBuilder requires a semiring kind"
        super().__init__(root=root, kind=kind)

    def __getitem__(self, head):
        assert not isinstance(head, (NodeRef, _Product)), \
            "head must be a hashable key, not an expression"
        _ = self.incoming[head]   # ensure the node is known
        return NodeRef(self, head)

    def __setitem__(self, head, rhs):
        if rhs is _IADD_SENTINEL:
            return                # __iadd__ already appended
        self._append_edge(head, rhs)

    def _append_edge(self, head, rhs):
        weight, body = self._normalize(rhs)
        self.edge(weight, head, *body)

    def _normalize(self, rhs):
        if isinstance(rhs, NodeRef):
            assert rhs.graph is self, "NodeRef belongs to a different graph"
            return self.kind.one, [rhs.key]
        if isinstance(rhs, _Product):
            weight = self.kind.one
            body = []
            for f in rhs.factors:
                if isinstance(f, NodeRef):
                    assert f.graph is self, "NodeRef belongs to a different graph"
                    body.append(f.key)
                else:
                    weight = weight * f
            return weight, body
        return rhs, []
