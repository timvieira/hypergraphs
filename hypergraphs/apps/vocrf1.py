from collections import defaultdict
from vocrf.util import prefix_closure, longest_suffix_in, last_char_sub_closure
from hypergraphs.pcfg import WCFG


class VoCRF(object):

    def __init__(self, sigma, C, states, Py, transition):
        self.C = C
        self.Py = Py

        self.sigma = list(sigma)
        self.states = list(states)
        self.transition = transition

        outgoing = defaultdict(list)
        for s in self.states:
            for a in self.Py[s]:
                outgoing[s].append((a, transition[s, a]))
        self.outgoing = outgoing

    @classmethod
    def from_contexts(cls, sigma, raw_contexts):
        "Create machine."

        C = set(last_char_sub_closure(sigma, prefix_closure(raw_contexts)))

        C.update((a,) for a in sigma)
        C.update(())

        # Set of states is C minus the last character.
        states = {c[:-1] for c in C}

        # Transition function.
        arcs = {s: [] for s in states}
        transition = {}
        for c in C:
            if len(c) == 0: continue
            s, a = c[:-1], c[-1]
            arcs[s].append(a)
            # Figure out where this action takes us.
            transition[s, a] = longest_suffix_in(c, states)

        # empty state has explicit transitions for each element of sigma.
        # TODO: This be a default arc (rho arc), right?
        for y in sigma:
            if y not in arcs[()]:
                arcs[()].append(y)

        return cls(sigma, C, states, arcs, transition)

    def graph(self, T, one, edge):
        G = WCFG()
        G.start = (0, ())
        G.edge(one, G.start)
        active = set([()])
        for t in range(1, T+1):
            new = set([])
            for s in active:
                for a, sp in self.outgoing[s]:
#                    print('transition:', s, a, sp)
                    G.edge(edge([t-1, s, a, sp]), (t, sp), (t-1, s))
                    new.add(sp)
            active = new

        G.root = (T+1, '</s>')
        for s in active:
            G.edge(one, G.root, (T, s))

        return G


def test():
#    sigma = 'abcdefg'
    sigma = 'ab'
    Ts = [
        'aaaa',
        'bbbb',
    ]

    if 0:
        Ts = [
            'aa',
            'ab',
            'ba',
            'bb',
        ]

    # Small gradient example
    from semirings import Count
    M = VoCRF.from_contexts(sigma, list(map(tuple, Ts)))
    G = M.graph(T=8, one=Count.one(), edge=lambda e: Count(1))
    #G.show()

    from hypergraphs.derivation import post_process2
    for x in G.sorted():

        def ff(e):
            x = ''.join(e.head[1])
            if any(x == y[:-1] for y in Ts):   # missing the action.
                return x
            else:
                return '-'

        d2 = post_process2(ff, x.data)
        print(d2)

    return


if __name__ == '__main__':
    test()
