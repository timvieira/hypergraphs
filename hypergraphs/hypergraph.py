from collections import defaultdict, namedtuple


Edge = namedtuple('Edge', 'weight, head, body')


class Hypergraph(object):

    def __init__(self, root=None):
        self.incoming = defaultdict(list)
        self.edges = []
        self.root = root
        self.kind = None

    def __repr__(self):
        return f'{self.__class__.__name__}({self.kind.__name__}, nodes={len(self.nodes)}, edges={len(self.edges)})'

    def edge(self, weight, head, *body):
        self.kind = type(weight)
        e = Edge(weight, head, body)
        self.incoming[e.head].append(e)
        self.edges.append(e)
        return e

    @property
    def nodes(self):
        return self.incoming.keys()

    def terminals(self):
        terminals = set()
        for e in self.edges:
            for b in e.body:
                if not self.incoming[b]:
                    terminals.add(b)
        return terminals

    def toposort(self):
        visited = set()

        def t(v):
            if v not in visited:
                visited.add(v)
                if self.incoming[v]:
                    for e in self.incoming[v]:
                        for u in e.body:
                            yield from t(u)
                    yield v

        assert self.root is not None
        return t(self.root)

    def graphviz(self, output):
        from arsenal.iterextras import window
        with open(output, 'w') as f:
            print('digraph {', file=f)
            terminals = set()
            for x in list(self.incoming):
                for e in self.incoming[x]:
                    print('  "%s" [label=\"\",shape=point];' % id(e), file=f)
                    print('  "%s" -> "%s";' % (id(e), e.head), file=f)
                    for b in e.body:
                        print('  "%s" -> "%s" [arrowhead=none];' % (b, id(e)), file=f)
                        if not self.incoming[b]:
                            terminals.add(b)
            if terminals:
                print(terminals)
                f.write('{ rank = same; %s; }\n' % ('; '.join('"%s"' % (x,) for x in terminals)))
                for a, b in window(sorted(terminals, key=lambda x: x[0]), 2):
                    f.write('"%s" -> "%s" [dir=none, style=invis, penwidth=1];\n' % (a, b))
                    f.write('{ rank = same; "%s"; "%s"; }\n' % (a,b))
            print('}', file=f)

    def show(self, prefix='/tmp/hypergraph', gopen=True):
        from os import system
        dot = f'{prefix}.dot'; svg = f'{prefix}.svg'
        self.graphviz(dot)
        system(f'(dot -Tsvg {dot} > {svg}) 2>/dev/null')
        if gopen: system(f'google-chrome {svg} 2>/dev/null &')
        return svg

    def display(self):
        "Visualize graphviz rendering in a Jupyter notebook."
        from IPython.core.display import display, HTML
        svg = open(self.show(gopen=False)).read()
        display(HTML(svg))

    def Z(self):
        "Evaluate the partition function (total score of root node)."
        return self.inside()[self.root]

    def inside(self):
        "Run inside algorithm on hypergraph."
        B = self.kind.chart()
        for x in self.toposort():
            for e in self.incoming[x]:
                v = self.kind.one
                for b in e.body:
                    v *= B[b]
                B[x] += e.weight * v
        return B

    # TODO: modify the outside algorithm to support non-AC multiplication.
    def outside(self, B):
        "Run outside algorithm on hypergraph."
        A = self.kind.chart()
        A[self.root] = self.kind.one
        for x in reversed(list(self.toposort())):
            for e in self.incoming[x]:
                # TODO: The code below is quadratic in the arity of the edge,
                # this can be improved to linear with the gradient-of-product
                # trick.  Or, equivalently, by binarizing the edges of the
                # graph.
                for y in e.body:
                    w = self.kind.one
                    for z in e.body:
                        if y == z:
                            w *= A[x]
                        else:
                            w *= B[z]
                    A[y] += e.weight * w
        return A

    def insideout(self, A, B, X, zero):
        """Inside-outside algorithm.

        - `X`: Function of the `edge => X`.

          Elements of X must form a K-module (where K is the type of `A` and
          `B`).  The key operation is left-multiplication by type `K` which
          distributes over addition: (x_1 + x_2) k_1 = x_1 k_1 + x_2 k_1.

        - `zero`: Allocate a zero of type `X`.

        """
        xhat = zero
        for e in self.edges:
            kbar = A[e.head]
            for b in e.body:
                kbar *= B[b]
            xhat += X(e) * kbar
        return xhat

    def _prune_topo(self):
        return self.prune_nodes(set(self.toposort()))

    def prune_topo(self, verbose=0):
        """
        Eliminate nodes/edges from hypergraph which don't feed into any valid
        derivations of the root node.
        """
        # TODO: we shouldn't need to run topo-pruning to fixed point.
        r = 0
        prev = self
        while True:
            if verbose:
                print('prune round', r, prev)
            curr = prev._prune_topo()
            if len(curr.edges) == len(prev.edges):
                break
            prev = curr
            r += 1
        return curr

    def prune_nodes(self, nodes):
        "Prune graph down to a set of nodes."
        g = Hypergraph(self.root)
        for e in self.edges:
            if e.head in nodes and all(b in nodes for b in e.body):
                g.edge(e.weight, e.head, *e.body)
        return g

    def apply(self, f):
        "Transform this hypergraphs's edge weights via `f(edge) -> weight`."
        H = self.__class__(self.root)
        for e in self.edges:
            w = f(e)
            if w is not None:
                H.edge(w, e.head, *e.body)
        return H

    def sorted(self):
        return self._sorted().Z()

    def _sorted(self):
        from hypergraphs.semirings import LazySort
        return self.apply(lambda e: LazySort(e.weight, e))
