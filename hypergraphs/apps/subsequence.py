from collections import namedtuple

align = namedtuple('align', 'x,y')
ε = None


def subsequence(a, b, w, Weight):
    N = len(a); M = len(b)
    c = Weight.chart()
    c[0, 0] = Weight.one
    for i in range(N+1):
        for j in range(M+1):
            if i < N and j < M:
                c[i+1, j+1] += c[i, j] * Weight.lift(w(a[i], b[j]), align(a[i], b[j]))
            if i < N:
                c[i+1, j] += c[i, j] * Weight.lift(w(a[i], ε), align(a[i], ε))
            if j < M:
                c[i, j+1] += c[i, j] * Weight.lift(w(ε, b[j]), align(ε, b[j]))
    return c[N, M]


def default_cost(a,b):
    if a == b:
        return 1.0
    elif a is ε or b is ε:
        return 0.1
    else:
        return 0.0


def pretty(score, path):
    top = []
    bot = []
    def p(z):
        if isinstance(z, align):
            top.append(z.x or ' ')
            bot.append(z.y or ' ')
        else:
            x,y = z
            p(x)
            p(y)
    p(path)
    print(f'alignment: {score:g}')
    print(f'  ^{"".join(top)}$')
    print(f'  ^{"".join(bot)}$')


def test():
    from hypergraphs.semirings import LazySort
    from hypergraphs.semirings.sampling.lazy2 import Sample
    from arsenal.iterextras import take

    # Check that we do not have duplicate alignments
    dups = set()
    for x in subsequence('abcabc', 'abcb', default_cost, LazySort):
        x = str(x.data)
        assert x not in dups
        dups.add(x)

    print('number of alignments', len(dups))

    K = 5
    print()
    print(f'Top K={K}')
    print('========')
    for x in take(K, subsequence('abcabc', 'abcb', default_cost, LazySort)):
        pretty(x.score, x.data)

    print()
    print(f'Samples K={K}')
    print('============')
    for score, data in take(K, subsequence('abcabc', 'abcb', default_cost, Sample)):
        pretty(score, data)

    print()


if __name__ == '__main__':
    test()
