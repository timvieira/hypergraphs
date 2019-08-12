import re
import numpy as np
from hypergraphs.hypergraph import Hypergraph
from collections import defaultdict, namedtuple

# XXX: this grammar class is probably overkill - we can just use an RHS dictionary.
class Grammar(object):

    def __init__(self, rules, root):
        nonterminals = defaultdict(list)
        body = defaultdict(list)
        for r in rules:
            nonterminals[r.head].append(r)
            body[r.body].append(r)

        self.preterm = defaultdict(list)
        self.r_y_xz = defaultdict(list)
        self.r_y_x = defaultdict(list)

        for r in rules:
            assert 1 <= len(r.body) <= 2
            if len(r.body) == 1:
                [_, _, [y]] = r
                if y in nonterminals:
                    self.r_y_x[y].append(r)
                else:
                    self.preterm[y].append(r)
            else:
                [_, _, [y,_]] = r
                self.r_y_xz[y].append(r)

        self.nonterminals = dict(nonterminals)
        self.body = body
        self.rules = rules
        self.root = root

    @classmethod
    def load(cls, source, root='ROOT'):
        rules = []
        for line in source.strip().split('\n'):
            x = re.findall('\S+', re.sub('#.*', '', line.strip()))
            if x:
                rules.append(Rule(np.log(float(x[0])), x[1], tuple(x[2:])))
        return cls(rules, root)


class Rule(namedtuple('Rule', 'weight, head, body')):
    @property
    def parent(self):
        return self.head
    @property
    def left(self):
        return self.body[0]
    @property
    def right(self):
        return self.body[1]


papa_grammar = Grammar.load("""
1       ROOT    S
1       S       S <.>
1       S       NP VP
1       NP      Det N
1       NP      NP PP
.25     VP      V NP
.75     VP      VP PP
1       PP      P NP
1       NP      Papa
1       NP      Sally
1       N       caviar
1       N       president
1       NP      president
1       N       spoon
1       N       sandwich
1       N       pickles
1       N       nose
1       V       spoon
1       V       ate
1       V       smelled
1       V       perplexed
1       P       with
1       P       under
.85     Det     the
.85     Det     a
.1      Det     his
1       <.>     .
""")


# XXX: Related to implementation in notes.parse module, but this one creates a
# hypergraph object (maybe that could be done with a the "free" semring?).
# XXX: One notable difference is that this implementation supports unrolling
# unary chains for a finite number of steps.
def parse_forest(sentence, grammar, steps=3):
    """Build parse forest for `sentence` under `grammar` using a few `steps` for
    time indexed unary steps (avoids cycles).

    """

    assert isinstance(sentence, list)
    N = len(sentence)
    g = Hypergraph()
    g.root = (0, N, grammar.root, steps-1)

    semione = 0.0
    span = np.empty((N,N+1), dtype=set)
    for I in range(N):
        for K in range(N+1):
            span[I,K] = set()

    for I in range(N):
        Y = sentence[I]
        K = I + 1
        # add terminals
        g.edge(semione, (I,K,Y,0))
        # add preterminals
        for r in grammar.preterm[Y]:
            X = r.parent
            g.edge(r.weight, (I,K,X,0), (I,K,Y,0))
            span[I,K].add(X)
        for T in range(steps-1):
            # initialize time step with current value (might get overwritten)
            for Y in set(span[I,K]):
                left = (I,K,Y,T)
                # free unary rule Y->Y
                g.edge(semione, (I,K,Y,T+1), left)
                for r in grammar.r_y_x[Y]:
                    X = r.parent
                    g.edge(r.weight, (I,K,X,T+1), left)
                    span[I,K].add(X)

    for w in range(2, N+1):
        for I in range(N-w + 1):
            K = I + w
            for J in range(I+1, K):
                for Y in span[I,J]:
                    left = (I,J,Y,steps-1)
                    for br in grammar.r_y_xz[Y]:
                        X = br.parent
                        Z = br.right
                        if Z not in span[J,K]:
                            continue
                        right = (J,K,Z,steps-1)
                        g.edge(br.weight, (I,K,X,0), left, right)
                        span[I,K].add(X)
            for T in range(steps-1):
                for Y in set(span[I,K]):
                    left = (I,K,Y,T)
                    # free unary rule Y->Y
                    g.edge(semione, (I,K,Y,T+1), left)
                    for r in grammar.r_y_x[Y]:
                        X = r.parent
                        g.edge(r.weight, (I,K,X,T+1), left)
                        span[I,K].add(X)

    return g

