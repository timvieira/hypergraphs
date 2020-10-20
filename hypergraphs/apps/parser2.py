"""
Simple semiring parser.
"""
from collections import defaultdict


def load_grammar(grammar):
    rhs = defaultdict(list)
    for line in grammar.strip().split('\n'):
        r = line.strip()
        if r.startswith('#'):  # skip comments
            continue
        if not r:              # skip empty lines
            continue
        r = r.split()
        rhs[tuple(r[1:])].append(r[0])
    return rhs


def parse(sentence, rhs, binary, unary, terminal, zero):
    n = len(sentence)
    c = defaultdict(lambda: zero)      # semiring zero
    span = defaultdict(set)
    for i, w in enumerate(sentence):
        k = i + 1
        # Terminal
        span[i,k].add(w)
        c[i,k,w] = terminal(sentence,w,i)
        # Pre-terminal rules
        for y in set(span[i,k]):
            for x in rhs[y,]:
                span[i,k].add(x)
                c[i,k,x] += c[i,k,y] * unary(sentence,x,y,i,k)
    for w in range(2, n+1):
        for i in range(n-w + 1):
            k = i + w
            # fill in cell with binary rules.
            for j in range(i+1, k):
                for y in span[i,j]:
                    for z in span[j,k]:
                        for x in rhs[y,z]:
                            span[i,k].add(x)
                            c[i,k,x] += c[i,j,y] * c[j,k,z] * binary(sentence,x,y,z,i,j,k)
    return c


#from arsenal.cache import memoize
#def rec(sentence, rhs, binary, unary, terminal):
#
#    @memoize
#    def p(i,k,x):
#        if k - i == 1:
#            y = sentence[i]
#            return unary(sentence,x,y,i,k) * terminal(sentence,y,i)
#
#        return sum(
#            p(i,j,y) * p(j,k,z) * binary(sentence,x,y,z,i,j,k)
#            for j in range(i+1, k)
#            for y,z in rhs[x]
#        )
#
#    return p(0, len(sentence), 'S')
