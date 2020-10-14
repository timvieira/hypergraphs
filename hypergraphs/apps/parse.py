import re
import numpy as np
from hypergraphs.pcfg import WCFG
from collections import defaultdict, namedtuple
from hypergraphs.semirings.logval import LogVal

Rule = namedtuple('Rule', 'weight, head, body')

# XXX: this grammar class is overkill - we can just use an RHS dictionary.
class Grammar:

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
            if not x: continue
            W, X, *Ys = x
            rules.append(Rule(LogVal.lift(float(W)), X, tuple(Ys)))
        return cls(rules, root)


def parse_forest(sentence, grammar, steps=1):
    """
    Build parse forest for `sentence` under `grammar` using a few `steps` for
    time indexed unary steps (avoids cycles).
    """

    assert isinstance(sentence, list)
    N = len(sentence)
    g = WCFG()
    g.root = (0, N, grammar.root, steps)

    one = LogVal.one
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


class papa:
    grammar = Grammar.load("""
    # rules ------------------
    1       ROOT    S   <.>
    1       S       NP  VP
    1       NP      Det N
    1       NP      NP  PP
    .25     VP      V   NP
    .75     VP      VP  PP
    1       PP      P   NP
    # vocabulary --------------
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
    sentence = 'Papa ate the caviar with the spoon .'.split()
    hypergraph = parse_forest(sentence, grammar, steps=1)


class abc:
    grammar = Grammar.load("""
    1       AB      A   B
    1       BC      B   C
    1       ABC     AB  C
    1       ABC     A   BC
    1       CD      C   D
    1       BCD     BC  D
    1       BCD     B   CD

    1       ABCD    ABC D
    1       ABCD    A   BCD
    1       ABCD    AB  CD

    1       A       a
    1       B       b
    1       C       c
    1       D       d
    """, root = 'ABCD')
    sentence = 'a b c d'.split()
    hypergraph = parse_forest(sentence, grammar, steps=0)
