"""Tests for the operator-overloading sugar on `HypergraphBuilder`."""

from itertools import combinations

import numpy as np

from hypergraphs.builder import HypergraphBuilder, _IADD_SENTINEL
from semirings import Float


# --- nullary / unary / binary ---------------------------------------------

def test_nullary_axiom():
    g = HypergraphBuilder(Float)
    g['a'] = 1.0
    assert len(g.edges) == 1
    e = g.edges[0]
    assert e.weight == 1.0
    assert e.head == 'a'
    assert e.body == ()


def test_unary_edge_uses_kind_one():
    g = HypergraphBuilder(Float)
    g['a'] = 1.0
    g['b'] += g['a']
    b_edges = [e for e in g.edges if e.head == 'b']
    assert len(b_edges) == 1
    assert b_edges[0].weight == Float.one
    assert b_edges[0].body == ('a',)


def test_binary_edge_with_weight():
    g = HypergraphBuilder(Float)
    g['a'] = 1.0
    g['b'] = 1.0
    g['c'] += 2.0 * g['a'] * g['b']
    c_edges = [e for e in g.edges if e.head == 'c']
    assert len(c_edges) == 1
    assert c_edges[0].weight == 2.0
    assert c_edges[0].body == ('a', 'b')


def test_scalar_position_independent():
    g = HypergraphBuilder(Float)
    g['a'] = 1.0
    g['b'] = 1.0
    g['c'] += 2.0 * g['a'] * g['b']
    g['d'] += g['a'] * 3.0 * g['b']
    g['e'] += g['a'] * g['b'] * 4.0
    ws = {e.head: e.weight for e in g.edges if e.head in ('c', 'd', 'e')}
    assert ws == {'c': 2.0, 'd': 3.0, 'e': 4.0}


def test_multiple_scalars_multiply_in_order():
    g = HypergraphBuilder(Float)
    g['a'] = 1.0
    g['h'] += 2.0 * 3.0 * g['a']
    e = next(e for e in g.edges if e.head == 'h')
    assert e.weight == 6.0
    assert e.body == ('a',)


def test_ternary_body_preserves_order():
    g = HypergraphBuilder(Float)
    g['a'] = 1.0; g['b'] = 1.0; g['c'] = 1.0
    g['h'] += g['a'] * g['b'] * g['c']
    e = next(e for e in g.edges if e.head == 'h')
    assert e.body == ('a', 'b', 'c')
    assert e.weight == Float.one


# --- `+=` vs `=` equivalence and self-assignment --------------------------

def test_iadd_and_assign_produce_same_edges():
    g1 = HypergraphBuilder(Float)
    g2 = HypergraphBuilder(Float)
    g1['a'] = 1.0; g2['a'] = 1.0
    g1['b'] = 2.0 * g1['a']
    g2['b'] += 2.0 * g2['a']
    assert [(e.weight, e.head, e.body) for e in g1.edges] \
        == [(e.weight, e.head, e.body) for e in g2.edges]


def test_self_loop_via_iadd():
    g = HypergraphBuilder(Float)
    g['a'] = 1.0
    g['a'] += g['a']
    loops = [e for e in g.edges if e.head == 'a' and e.body == ('a',)]
    assert len(loops) == 1


def test_self_loop_via_assign():
    g = HypergraphBuilder(Float)
    g['a'] = 1.0
    g['a'] = g['a']
    loops = [e for e in g.edges if e.head == 'a' and e.body == ('a',)]
    assert len(loops) == 1


def test_iadd_sentinel_is_noop_in_setitem():
    # The return value of __iadd__ is the sentinel; Python then calls
    # __setitem__(head, sentinel). That call must not add an edge.
    g = HypergraphBuilder(Float)
    g['a'] = 1.0
    before = len(g.edges)
    g[None] = _IADD_SENTINEL
    assert len(g.edges) == before


# --- interop with numpy scalars -------------------------------------------

def test_numpy_scalar_on_left():
    g = HypergraphBuilder(Float)
    g['a'] = 1.0
    w = np.float64(0.5)
    g['b'] += w * g['a']
    e = next(e for e in g.edges if e.head == 'b')
    assert e.weight == 0.5
    assert e.body == ('a',)


def test_numpy_scalar_on_right():
    g = HypergraphBuilder(Float)
    g['a'] = 1.0
    w = np.float64(0.5)
    g['b'] += g['a'] * w
    e = next(e for e in g.edges if e.head == 'b')
    assert e.weight == 0.5
    assert e.body == ('a',)


# --- validation -----------------------------------------------------------

def test_kind_is_required():
    try:
        HypergraphBuilder(None)
    except AssertionError:
        return
    assert False, "HypergraphBuilder(None) should have raised"


def test_cross_graph_noderef_rejected():
    g1 = HypergraphBuilder(Float)
    g2 = HypergraphBuilder(Float)
    g1['a'] = 1.0
    try:
        g2['b'] += g1['a']
    except AssertionError:
        return
    assert False, "mixing NodeRefs from two graphs should have raised"


def test_head_may_not_be_expression():
    g = HypergraphBuilder(Float)
    g['a'] = 1.0
    try:
        g[g['a']]
    except AssertionError:
        return
    assert False, "NodeRef-as-head should have raised"


# --- end-to-end: subset-sum recurrence ------------------------------------

def test_subset_graph_matches_brute_force():
    """G[K, N] should equal sum over size-K subsets of products of w[i]."""
    rng = np.random.default_rng(0)
    N, K = 6, 3
    w = rng.uniform(0, 1, size=N)

    g = HypergraphBuilder(Float, root=(K, N))
    for n in range(N):
        g[0, n] = 1.0
    for k in range(1, K + 1):
        for n in range(N):
            g[k, n + 1] += g[k, n]
            g[k, n + 1] += w[n] * g[k - 1, n]

    expected = sum(
        float(np.prod([w[i] for i in s]))
        for s in combinations(range(N), K)
    )
    assert abs(g.Z() - expected) < 1e-12


def test_subset_graph_edge_count():
    # N rows of axioms + K*N unary (carry) edges + K*N scalar edges
    N, K = 4, 2
    w = np.arange(1, N + 1, dtype=float)

    g = HypergraphBuilder(Float, root=(K, N))
    for n in range(N):
        g[0, n] = 1.0
    for k in range(1, K + 1):
        for n in range(N):
            g[k, n + 1] += g[k, n]
            g[k, n + 1] += w[n] * g[k - 1, n]

    assert len(g.edges) == N + 2 * K * N


if __name__ == '__main__':
    funcs = [f for name, f in sorted(globals().items()) if name.startswith('test_')]
    for f in funcs:
        f()
        print(f'ok  {f.__name__}')
    print(f'\n{len(funcs)} passed')
