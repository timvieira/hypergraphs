import re
import numpy as np
from hypergraphs.pcfg import WCFG
from collections import defaultdict, namedtuple
from hypergraphs.semirings.logval import LogVal

# XXX: this grammar class is overkill - we can just use an RHS dictionary.
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
                rules.append(Rule(LogVal.lift(float(x[0])), x[1], tuple(x[2:])))
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

1       ROOT    S   <.>
1       S       NP  VP
1       NP      Det N
1       NP      NP  PP
.25     VP      V   NP
.75     VP      VP  PP
1       PP      P   NP

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
def parse_forest(sentence, grammar, steps=1):
    """Build parse forest for `sentence` under `grammar` using a few `steps` for
    time indexed unary steps (avoids cycles).

    """

    assert isinstance(sentence, list)
    N = len(sentence)
    g = WCFG()
    g.root = (0, N, grammar.root, steps)

    one = LogVal.one()
    span = np.empty((N,N+1), dtype=set)
    for I in range(N):
        for K in range(N+1):
            span[I,K] = set()

    def unary(I,K):
        for T in range(steps):
            # initialize time step with current value (might get overwritten)
            for Y in set(span[I,K]):
                # free unary rule Y->Y
                edge(one, (I,K,Y,T+1), (I,K,Y,T))
                for [W, X, _] in grammar.r_y_x[Y]:
                    edge(W, (I,K,X,T+1), (I,K,Y,T))

    def edge(w, x, *ys):
        (I,K,X,_) = x
        g.edge(w, x, *ys)
        span[I,K].add(X)

    for I in range(N):
        Y = sentence[I]
        K = I + 1
        # add terminals
        g.edge(one, (I,K,Y,0))
        # add preterminals
        for [W,X,_] in grammar.preterm[Y]:
            edge(W, (I,K,X,0), (I,K,Y,0))
        unary(I,K)

    for w in range(2, N+1):
        for I in range(N-w + 1):
            K = I + w
            for J in range(I+1, K):
                for Y in span[I,J]:
                    for [W, X, [_,Z]] in grammar.r_y_xz[Y]:
                        if Z not in span[J,K]: continue
                        edge(W, (I,K,X,0), (I,J,Y,steps), (J,K,Z,steps))
            unary(I,K)

    return g
