# Pre-registration — does the coverage rule transfer to KnowledgeDrift?

Written 2026-09-20, **before the rule was run against these probes even once.**
Nothing below was chosen after seeing a result. The commitments here are what
make the outcome informative either way.

## The question

The corpus-coverage abstention rule (`team/S11-ABSTAIN3/declaration.json`)
declined 5/5 irrelevant declaration queries and 3/5 irrelevant holdout queries
while losing 0/5 useful retrievals on each — on ten cases this project wrote
itself. Five independently tested implementations scored **0/40 abstentions** on
the external KnowledgeDrift sample (`team/S10-KD-CROSS/verdict.json`).

Does the rule, unchanged, decline irrelevant questions on someone else's frozen
cases without discarding useful answers?

## The rule, frozen and unmodified

From `S11-ABSTAIN3/declaration.json`, `rule.family = corpus-coverage`,
`rule.decision = supported_fraction_lt_threshold`:

1. Tokenise the query.
2. Drop the 68 declared `content_stopwords`.
3. `supported` = remaining terms occurring in at least
   `min_document_frequency` (= 1) corpus documents.
4. `supported_fraction = supported / remaining`.
5. Abstain when `supported_fraction < threshold`.

Declared threshold grid, unchanged: **0.0, 0.25, 0.5, 0.75, 1.0**.
Retrieval where required: BM25, `k1 = 1.2`, `b = 0.75`, `top_k = 1`, as declared.

**No parameter is tuned here.** The stopword list, the frequency floor, the
decision form and the grid are all taken as they stand.

## The inputs, frozen

- Worlds, sha-pinned in `S10-KD-CROSS/declaration.json`:
  `knowledgedrift-500-seed1-v2.json` (dc5af10e…) and
  `knowledgedrift-500-seed2-v2.json` (29765562…), upstream commit
  `edff308ea6ab331dbb24e0ab5ac29717d88b29f0`.
- The 120-probe item list, byte-identical to `S10-KD-CROSS/items.jsonl`:
  40 Retrieval, 40 Abstention, 40 Rationale, across the two seeds.
- Query text comes from each probe's `recall` op in the world's op stream.
  The corpus is the records inscribed by that stream.

The sample is **not** re-drawn. If a probe cannot be resolved, it is reported as
unresolved, never silently replaced.

## What is measured, and reported separately

Two numbers, never combined into one score:

1. **Correct abstentions** — of the 40 Abstention probes (`expect: control`),
   how many the rule declines. Higher is better.
2. **Useful retrievals lost** — of the 80 Retrieval and Rationale probes
   (`expect: gold` / `expect: linked`), how many the rule declines and so
   discards an answer it should have given. Lower is better.

Reported per threshold, and broken out per family and per seed. A single
blended figure is not reported, because the tradeoff is the finding.

## Committed before results

- **Every threshold in the grid is reported.** No threshold may be selected
  after seeing outcomes. If more than one meets the bar, that is reported as
  "no winning threshold established", exactly as S11-ABSTAIN3 did.
- **The comparison is against 0/40.** Five implementations declined nothing on
  this sample. That is the baseline the rule must beat to have transferred.
- **A null is publishable and expected to be publishable.** If the rule
  declines nothing, or declines everything, or only buys abstentions by
  discarding useful answers, that is the result and it is reported as the
  finding of the row.

## The bar, set now

**Transfer is demonstrated** if at least one threshold in the declared grid
gives correct abstentions materially above the 0/40 floor while losing no more
than **10% (8 of 80)** of useful retrievals.

**Transfer fails** if no threshold clears that, and the row reports why: too few
abstentions, or too many useful answers destroyed to buy them.

**Neither outcome is a product recommendation.** This measures one rule's
behaviour on one external sample. It establishes nothing about whether memory
improves real work.

## Known limitations, stated in advance

- Abstention probes carry no query-specific gold; correctness is "declined or
  not", not "declined for the right reason".
- 40 probes per family across two seeds is a small sample; no confidence
  interval is claimed.
- The benchmark's author has a competing system in its own published ranking.
- Vocabulary coverage cannot catch a question phrased entirely in words the
  corpus contains but does not answer. That hole is not closed by this test.

## Verification

An independent seat (corvid-dsh) re-runs from this declaration and the pinned
shas, and checks the two counts. The author does not verify their own row.
