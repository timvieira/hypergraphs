from collections import namedtuple

align = namedtuple('align', 'x,y')
ε = None


def subsequence(a, b, w, Weight):
    N = len(a); M = len(b)
    c = Weight.chart()
    c[N, M] = Weight.one
    for i in reversed(range(N+1)):
        for j in reversed(range(M+1)):
            if i < N and j < M:
                c[i, j] += Weight.lift(w(a[i], b[j]), align(a[i], b[j])) * c[i + 1, j + 1]
            if i < N:
                c[i, j] += Weight.lift(w(a[i], ε), align(a[i], ε)) * c[i + 1,     j]
            if j < M:
                c[i, j] += Weight.lift(w(ε, b[j]), align(ε, b[j])) * c[    i, j + 1]
    return c[0, 0]


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
