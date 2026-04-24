# TODO

Coherence and completeness work for the `hypergraphs` repo. Organized by theme;
roughly ordered within each section from highest leverage to lowest.

## Documentation

- [ ] **Terminology consistency pass across the repo.** Pick one word for
  each concept and use it everywhere — docstrings, variable names, method
  names, README prose. Known offenders:
  - `.score` (MaxPlus) vs `.cost` (MinPlus) vs `.d` (generic) for the
    scalar accessor on a semiring element — no uniform interface. Either
    add `__float__` / a shared `.value` property in `semirings`, or pick
    one accessor name and rename the others (this also affects the
    README example).
  - "body" (in `Edge` / `Hypergraph`) vs "tail" (common in the
    hypergraph literature) vs "children" (in the `PCFG.sample` /
    derivation code). Pick one.
  - "terminal" — the code's `Hypergraph.terminals()` returns nodes with
    no incoming hyperedge, but the formal DP treatment often uses
    "terminal" to mean "a hyperedge with empty body". The README now
    follows the latter convention; the code still uses the former.
    Reconcile.
  - "weight" / "score" / "cost" used interchangeably. In prose and API,
    use "weight" for the abstract semiring value and reserve "score" /
    "cost" for MaxPlus / MinPlus specifically.
  - Forest vs hypergraph — often used interchangeably, but "forest"
    should mean an acyclic hypergraph (or the instantiated derivations
    of one). Nail this down in a glossary.
  Ideally: add a short glossary section once the canonical names are
  picked, and enforce with `git grep` audits.
- [ ] Auto-generate `README.md` so it can't go stale. The body should be
  assembled from a template plus machine-extracted content: the quickstart
  example should be executed (doctest / `jupyter nbconvert --execute` or a
  simple `exec`-and-capture script) so its output is embedded, and the
  graphviz SVG should be re-rendered on build. Wire this into a pre-commit
  hook or a `make readme` target so the committed README is always the
  executed one. The handwritten README below becomes the template.
- [ ] Rewrite the README template with:
  - one-paragraph pitch (semiring-generic DP over hypergraphs)
  - install instructions, including the external `semirings` dependency
  - 10-line hello-world example (build a forest, run `inside`, run `sorted`)
  - links to the demos in `demos/` with one-line descriptions each
  - link to Li & Eisner and Dyer papers with a pointer to the tests that
    implement them (`test/test_expectation.py`, `test/test_mert.py`)
- [ ] Add module-level docstrings to `hypergraphs/hypergraph.py` and
  `hypergraphs/pcfg.py` documenting the semiring protocol
  (`kind.chart`, `kind.one`, `*`, `+`, `+=`).
- [ ] Document how a user plugs in their own semiring (minimal interface + an
  example).
- [ ] Add `CITATION.cff` so GitHub surfaces "Cite this repository" natively
  (keep the bibtex in the README too).

## Structure / layout

- [ ] Decide the fate of `hypergraphs/builder.py` (untracked WIP that defines a
  second `Hypergraph` class via `+=` / `*` overloading). Options: merge its
  ideas into the canonical `Hypergraph`, rename to `hypergraphs.builder.Builder`
  and export it, or delete. Currently it shadows the main class name and is
  confusing.
- [ ] Support a declarative front-end for building hypergraphs — e.g. via
  [`dyna-pi`](https://github.com/timvieira/dyna-pi) or an equivalent
  weighted-logic-programming DSL — so users write the recurrence as inference
  rules and the hypergraph is constructed for them. This is the natural
  high-level counterpart to the imperative `g.edge(...)` API and to the
  `+=`/`*` overloading in `builder.py`; picking it up would also give the
  repo a clean story for "how do I express my DP?" that scales past toy
  examples.
  - **Schematic hyperedges (variables).** Dyna's EDSL lets rules carry
    variables — a single CKY rule written as

    ```
    chart[I, X, K] += chart[I, Y, J] * chart[J, Z, K] * rule(X, Y, Z)
    ```

    where `I, J, K, X, Y, Z` are `Var`s and `chart` is a `dyna.Program`,
    stands for a (potentially huge) family of ground hyperedges. The
    backend grounds them on demand rather than materializing the whole
    family up front. Worth supporting here: both the rule-with-variables
    surface syntax and the grounding-on-demand backend (ties into the
    lazy / infinite-hypergraph items above). See `~/projects/dyna-pi`.
  - **Cross-hypergraph communication.** Dyna programs can reference items
    from other programs (items of one `dyna.Program` appearing as
    antecedents in another's rules), so multiple hypergraphs can be
    composed and iterated together. A minimal analogue here would be a
    way for two `Hypergraph` objects to share a subset of nodes / wire
    up a handful of cross-edges — useful for pipelining (e.g. a tagger
    forest feeding into a parser forest) and for the kinds of joint
    inference where a monolithic hypergraph would be unwieldy.
- [ ] Move `notes/` (align, insideout, insideout2, insideout3, lp, parse,
  sample) somewhere that signals "scratch": promote the useful bits into
  `hypergraphs/` or `demos/`, and either delete the rest or relocate to
  `scratch/` and gitignore it.
- [ ] `demos/citations/` has a `.py` and data but no notebook — either add a
  demo notebook or promote `citations.py` to `hypergraphs/apps/`.
- [ ] Delete the duplicate `PCFG.sample` method in `hypergraphs/pcfg.py` (the
  one at line ~47 is shadowed by the one at line ~60).
- [ ] Introduce a first-class `Derivation` class. Today derivations are
  represented as nested tuples/lists of `Edge`s (see the output of
  `g.sorted()` and the ad-hoc `post_process` / `post_process2` helpers in
  `hypergraphs/derivation.py`). A proper `Derivation` type should carry the
  head node, the hyperedge chosen, and its child derivations, with methods
  for weight, yield/leaves, size, tree rendering, equality/hashing, and an
  nltk-Tree conversion — and the `post_process*` helpers collapse into
  methods on it.
- [ ] Make sure `hypergraphs.egg-info/` is gitignored.

## Testing / CI

- [ ] Convert `test/` to a proper pytest layout:
  - rename `test/kbest.py` to `test_kbest.py` (or delete if redundant)
  - add `conftest.py` / `pytest.ini` / `pyproject.toml` test config
  - make sure every `test_*.py` runs under `pytest test/`
- [ ] Add a GitHub Actions workflow that runs the test suite on push / PR
  against a pinned `semirings` version.
- [ ] Add a smoke test that imports every module in `hypergraphs/apps/` so
  regressions in the demos don't go unnoticed.

## Packaging

- [ ] Replace `setup.py` with `pyproject.toml` (PEP 621).
- [ ] Declare `install_requires`: `numpy`, `nltk`, `arsenal`, `semirings`,
  with version bounds.
- [ ] Pin the minimum Python version.

## Algorithmic TODOs (already flagged in the code)

- [ ] `Hypergraph.outside` is O(arity²) per edge. Replace with the
  gradient-of-product trick (or binarize edges). See comment at
  `hypergraphs/hypergraph.py:109`.
- [ ] `Hypergraph.outside` comment notes it does not yet support non-AC
  multiplication. Either implement or document the restriction.
- [ ] `Hypergraph.prune_topo` runs to a fixpoint (`hypergraph.py:152`). Work
  out why one pass isn't enough and fix so it isn't needed.
- [ ] `hypergraphs/pcfg.py`: the `PDA`-based sampler references a
  `DottedRule.expand_next` and a free `new()` that don't exist — looks
  half-finished. Finish or remove.
- [ ] `Hypergraph.sorted()` (and the underlying `_sorted` / `LazySort`
  wrapping) always enumerates in a MaxPlus-oriented order regardless of
  the inner semiring — under MinPlus you get the *worst* item first.
  Expose an explicit direction (`ascending=False`) or wrap with
  `Dual(...)` when the inner semiring's $\oplus$ is min.
- [ ] Support lazily-materialized hypergraphs. Allocating concrete `Edge`
  objects is often the dominant cost, and most algorithms don't need them
  materialized — CKY, segmentation, subsets-of-size-$K$, matrix-chain, and
  friends can evaluate inside (and $k$-best, sampling, marginals) directly
  off the recurrence, visiting each hyperedge once without storing it.
  Proposed shape: an abstract `Hypergraph` interface where the concrete
  class provides `toposort` and, for each node, a generator of
  `(weight, body_nodes)` triples; the current `Hypergraph` is the eagerly
  materialized implementation, and a `LazyHypergraph` (or a decorator that
  takes a recurrence function) is the on-the-fly one. Inside/outside/
  $k$-best/sampling should work uniformly against the interface.
  Double-visit algorithms (outside, inside–outside) need either a memoized
  second pass or explicit materialization of the edges discovered during
  the inside pass — worth spelling out which algorithms are single-visit
  vs which require materialization.
- [ ] Exploration of large / infinite hypergraphs, in the spirit of Dynasty
  (Eisner et al.) and the weighted-deduction / agenda-driven line of work.
  When the hypergraph is too large to materialize — or is genuinely
  infinite (e.g. parsing with an unbounded grammar, best-first search over
  a search graph) — inside is the wrong algorithm; you want agenda-driven
  priority-queue search, generalizing Dijkstra/Knuth's algorithm to
  weighted hypergraphs and producing the best-scoring derivation (or the
  top-$k$) by expanding only the antecedents that can improve it.
  Requires: a priority semiring (monotone, "superior" in Knuth's sense),
  an agenda data structure, and a way for a lazy hypergraph to yield
  antecedents on demand. This composes with the lazy-materialization item
  above — agenda search is the natural consumer of an implicitly-defined
  hypergraph.
- [ ] Support cycles in `Hypergraph`. The current `inside` / `outside` use
  `toposort()` and therefore assume a DAG; this is also why
  `hypergraphs/apps/kleene.py` operates on a matrix rather than a
  `Hypergraph`. Bringing `kleene` in (and making the repo cover the
  shortest-path / Kleene–Gauss case uniformly) requires a cyclic solver.
  - SCC analysis is a prerequisite: condense the hypergraph into its
    SCC-DAG, run the existing acyclic inside/outside over the condensation,
    and inside each non-trivial SCC solve a closed-semiring fixed point
    (Kleene / Gauss–Jordan using `Weight.star`, or iterate to convergence
    when `star` isn't available). `semirings` already exposes `Star` /
    `kleene` / `scc_decomposition`, so the building blocks are in place.
  - Consider Newton's algorithm for the SCC solves. For the polynomial
    systems that arise from hypergraph fixed points over an
    $\omega$-continuous semiring (Esparza–Kiefer–Luttenberger), Newton
    converges dramatically faster than Kleene iteration — often in a
    handful of steps where Kleene needs many — and degenerates to
    Gauss–Jordan on linear SCCs. Worth pursuing for SCCs that don't have
    a nice closed-form `star`.
  - Until this lands, `apps/kleene.py` is an outlier (matrix-only, doesn't
    use `Hypergraph`), and it isn't obvious it belongs in this repo.

## Catalog / library of constructions

- [ ] Build out a catalog of common hypergraph constructions as a first-class
  module (not scattered demos). Each entry takes inputs and returns a
  `Hypergraph` ready to run inside/outside/$k$-best/sample against any
  semiring. Where an existing file already implements one of these (e.g.
  `apps/segmentation.py`, `apps/subsets.py`, `demos/Matrix-chain-*.ipynb`),
  move it into the catalog and have the demo/notebook import from there
  instead of re-deriving it.

  **Parsing and grammars (NLP).**
  - CKY / Earley / weighted CFG parse forest
  - Bar-Hillel construction (WCFG $\cap$ WFSA)
  - Eisner's algorithm for projective dependency parsing
  - Chu–Liu–Edmonds for non-projective (MST) dependency parsing
  - TAG / LCFRS / synchronous CFG parse forests
  - Inside–outside for PCFG estimation (EM)
  - Supertagging / hypertagger forests
  - ITG (Wu) for bitext alignment

  **Machine translation and decoding.**
  - Hiero / SCFG translation forests (Chiang)
  - Tree-to-string / string-to-tree / tree-to-tree transducer forests
    (Galley et al.; xT, xR)
  - Phrase-based MT decoding lattice
  - Forest rescoring / cube pruning (Huang & Chiang)
  - Minimum Bayes risk decoding over a forest
  - Lattice / confusion-network decoding (Mangu et al.)

  **Finite-state and sequences.**
  - WFSA intersection, WFST composition, determinization residuals
  - Regular-expression $\to$ NFA construction (Thompson / Glushkov)
  - HMM / linear-chain CRF / semi-CRF forward lattices
  - CTC / RNN-T lattices for speech
  - Edit distance and sequence alignment (Needleman–Wunsch,
    Smith–Waterman, affine-gap, Sankoff)
  - Sequence segmentation
  - Subsequences, subsets of size $K$

  **Classical algorithms as hypergraphs.**
  - Single-source shortest path / algebraic path problem
  - Matrix-chain multiplication (note: `demos/Matrix-chain-multiplication.ipynb`
    has a chart-builder version via `Weight.chart()` that doesn't return a
    `Hypergraph`; the catalog entry should return a `Hypergraph` so the
    README example can `from hypergraphs.catalog import matrix_chain`
    instead of re-deriving the recurrence inline)
  - Optimal binary search tree
  - Polygon triangulation
  - 0/1 knapsack and its variants
  - Permutations / permanent
  - Shortest hyperpath / Kleene–Gauss (once cycles are supported)

  **Beyond NLP.**
  - AND/OR graphs for planning and two-player games (minimax as a
    hypergraph evaluation)
  - Variable elimination / junction-tree inference for PGMs (cliques as
    hyperedges)
  - Dynamic programming over tree decompositions / hypertree
    decompositions for CSP and database-query evaluation
  - RNA secondary-structure prediction (Nussinov, Zuker)
  - Progressive multiple-sequence alignment
  - Boolean formula / circuit evaluation on bounded-treewidth inputs
  - Pareto / multi-objective decoding forests

- [ ] Type hints on the public API (`Hypergraph`, `WCFG`, `PCFG`, `Edge`).
- [ ] A short "semirings cookbook" demo notebook showing the same forest
  evaluated under Viterbi, log, expectation, MERT, and k-best semirings
  side-by-side — this is the repo's main selling point and there's no single
  place that showcases it.
- [ ] Benchmarks against a binarized/Cython baseline to quantify the
  clarity-vs-performance trade-off the README advertises.
