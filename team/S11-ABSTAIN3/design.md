# S11-ABSTAIN3 design — S12-2 build (kiln-flash, preregistered before any run)

Row: QUEUE S12-2 (BM25 abstention, third declared relevance decision with
held-out cases). Gate: this directory's check.py, sha256
`522125d698bb44ebf28ffabae0176924595ccd7e7d2a3ac4bbafb24af83bd35d`,
pinned at first read 2026-09-19 16:27 PDT and re-checked after every run
(receipt team/CORVID-S12-2G-VERIFY.md, VERIFIED PASS 16:21 PDT).

## Prior measurements this run must speak against (RE-MEASUREMENT RULE)

- team/S6-SELECTIVITY/results.jsonl, sha256
  `5f3f14fc2f9b609b9153a8fbe8a3cba33aa8bcbc39689e561e6828af436196ab`:
  bm25 arm retrieves 5/5 useful, abstains 0/5 irrelevant.
- team/S7-BM25-PREFILTER/verdict.json (refuted): stopword filter rejected
  0/5 irrelevant, lost 1 useful retrieval (sel-003 regressed).
- team/S10-BM25-ABSTAIN2/verdict.json (refuted): score-margin rule rejected
  2/5 at its declared threshold 1.0 and lost 1 useful; grid 0.5 -> 0/0,
  1.0 -> 2/1, 1.5 -> 5/2.

Neither refuted mechanism is reused: this run declares a third family.

## Declared rule (third family: corpus-coverage)

Abstain exactly when the fraction of the query's distinct content tokens
whose document frequency in the case's own store is at least
`min_document_frequency` falls strictly below the threshold:

- `min_document_frequency = 1`: a content token is supported when the case
  store knows it at all (least-assumption support; no second-document
  demand). The grid explores thresholds, not df.
- `content_stopwords`: the sorted function-word list below — articles,
  conjunctions, prepositions, auxiliaries, pronouns, wh-question words,
  quantifiers. Declared as a list, not built per-case; no token is removed
  from the BM25 query (the retriever still scores every token, including
  repetitions), so this is not the refuted token filter. No score, rank, or
  distribution is read anywhere in the rule, so this is not the refuted
  margin family.

Stopword list (fixed): a an and are as at be been but by can did do does for
from had has have how in into is it its many much of off on or our out over
own should so some such than that the their them then there these they this
those to too up was we were what when where which who whom why will with
without would your

## Declared BM25 baseline (for comparability with the priors)

algorithm bm25, k1 1.2, b 0.75, top_k 1 — the standard parameters, matching
the verified gate's documented replay semantics (idf = log(1 + (N - df +
.5)/(df + .5)), all query tokens including repetitions, document-ID tie
breaking, no result when all scores are zero).

## Declared threshold grid (fixed before any run)

[0.0, 0.25, 0.5, 0.75, 1.0] — even spacing over the full [0, 1] range of the
coverage fraction. Declared from the shape of the rule (a fraction) and its
boundary cases on the declaration set, never as a menu: the whole grid is
reported as data on both sets and no threshold is selected in the report.

Honest prediction, registered before the run, from declaration-set coverage
values alone (useful 0.833/0.800/0.500/0.750/0.571; irrelevant
0.000/0.000/0.250/0.400/0.000): thresholds in (0.4, 0.5] should reject the
zero-support and weakly-supported irrelevant queries (3-4 of 5) while
keeping every useful retrieval at or above coverage 0.5; the strict
less-than boundary means sel-003 (coverage exactly 0.5) and sel-008
(exactly 0.25) sit exactly on grid points and their fate at those points is
retrieve by the declared comparison. Whether the rule survives depends on
the holdout, which is sealed and unread: if its irrelevant queries are
zero-support like the declaration set's three, rejection survives at safe
thresholds; if they carry partial support, rejection may collapse to zero
at the thresholds that lose nothing. Both outcomes are reportable results.

## Pre-registered success bar (both sides, both sets)

Survival iff at least one preregistered threshold achieves, on the
declaration set, at least 1 irrelevant rejected and 0 useful lost, AND on
the holdout set, at least 1 irrelevant rejected and 0 useful lost — the
same two-sided demand the refuted margin arm failed, extended to require it
to hold out of sample. Anything else is honestly refuted. The verdict is
that bar's output applied to the whole grid, not a judgement call.

## Provenance commitments

- Declaration cases are converted faithfully from the frozen
  team/S6-SELECTIVITY/corpus.jsonl, sha256
  `5a8668f73383ea1acc4806a31df9240cc0eb9186a7be69385a8f23e8be2024be`
  (matches the pin recorded in S10-BM25-ABSTAIN2/declaration.json), with
  relevance labels assigned by reading: sel-001-r2, sel-002-r1, sel-003-r2,
  sel-004-r3, sel-005-r2 are the current answers to their queries (each
  store's stale/superseded near-miss is deliberately not labeled); the five
  abstain cases label empty. A pre-declaration check (declaration set only)
  confirmed the baseline top-1 equals each labeled document on 5/5 useful
  cases, so the S6 5/5 baseline shape is preserved at threshold 0.
- Generator pinned before holdout freeze: {algorithm: coverage-cases-v1,
  seed: 20260919, count: 10}. The holdout file is materialized mechanically
  from that pin, hashed, and its contents are not displayed or read by the
  declarer before declaration.json is final; only its sha256 crosses that
  boundary (the declaration is written against the original ten cases
  only).
- Execution: local, $0, zero LLM calls, S7-1 declare-then-run with
  SHA-bound rows; the runner computes every row and report counter with its
  own implementation of the gate's documented formulas, and the verified
  gate independently replays both sets case by case.
