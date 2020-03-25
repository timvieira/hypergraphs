from collections import defaultdict, namedtuple


Edge = namedtuple('Edge', 'weight, head, body')


class Hypergraph(object):

    def __init__(self):
        self.incoming = defaultdict(list)
        self.edges = []
        self.root = None
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
        self.graphviz(prefix + '.dot')
        system('(dot -Tsvg {prefix}.dot > {prefix}.svg) 2>/dev/null'.format(prefix=prefix))
        if gopen:
            system('google-chrome {prefix}.svg 2>/dev/null &'.format(prefix=prefix))

    def Z(self):
        "Evaluate the partition function (total score of root node)."
        return self.inside()[self.root]

    def inside(self):
        "Run inside algorithm on hypergraph."
        B = defaultdict(self.kind.zero)
        for x in self.toposort():
            for e in self.incoming[x]:
                v = e.weight
                for b in e.body:
                    v = v * B[b]
                B[x] += v
        return B

    def outside(self, B):
        "Run outside algorithm on hypergraph."
        A = defaultdict(self.kind.zero)
        A[self.root] = self.kind.one()
        for v in reversed(list(self.toposort())):
            for e in self.incoming[v]:
                for u in e.body:
                    z = A[v] * e.weight
                    for w in e.body:
                        if w != u:
                            z = z * B[w]
                    A[u] += z
        return A

    def insideout(self, A, B, X, zero):
        """Inside-outside algorithm.

        - `X`: Function of the `edge => X`.

          Elements of X must form a K-module (where K is the type of `A` and
          `B`).  The key operation is left-multiplication by type `K` which
          distributes over addition: (x_1 + x_2) k_1 = x_1 k_1 + x_2 k_1.

        - `zero`: Allocate a zero of type `X`.

        """
        xhat = zero()
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
        g = Hypergraph()
        for e in self.edges:
            if e.head in nodes and all(b in nodes for b in e.body):
                g.edge(e.weight, e.head, *e.body)
        g.root = self.root
        return g

    def apply(self, f):
        "Transform this hypergraphs's edge weights via `f(edge) -> weight`."
        H = self.__class__()
        H.root = self.root
        for e in self.edges:
            w = f(e)
            if w is not None:
                H.edge(w, e.head, *e.body)
        return H

    def sorted(self):
        from hypergraphs.semirings.lazysort import BaseCase
        return self.apply(lambda e: BaseCase(e.weight, e)).Z()
