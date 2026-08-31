# Baseline findings

These results are a harness sanity check, **not** the memory-system bake-off yet. Only local deterministic baselines were executable in this sandbox.

## Headline

| Provider | Hit@5 | MRR | All-relevant@5 | Prohibited@5 ↓ | Useful-before-harmful | Negative empty-rate |
|---|---:|---:|---:|---:|---:|---:|
| bm25 | 0.917 | 0.844 | 0.792 | 0.125 | 0.800 | 0.000 |
| dense_lsa | 0.958 | 0.837 | 0.958 | 0.125 | 0.800 | 0.500 |
| hybrid_rrf | 0.958 | 0.856 | 0.917 | 0.125 | 0.733 | 0.000 |

## What the baselines already reveal

- Simple lexical/LSA retrieval is strong on this small corpus, so a sophisticated engine needs to win on **temporal correctness, conflict handling, multi-hop completeness, procedural success-vs-failure ranking, or learning over time**, not merely Hit@5.
- All three simple baselines surface stale/failed evidence (`prohibited@5 = 0.125` mean). That is intentionally a major benchmark axis.
- The lexical baseline misses some multi-hop companions even when it finds one correct fact; `all-relevant@5` catches this.
- Negative/unanswerable behavior is separated from normal retrieval because many memory engines always return top-k evidence.
- The toy adaptive diagnostic moves `useful-before-harmful` from 0.80 to 1.00 after verified feedback learned from **training-only paraphrases** and measured on disjoint held-out query wording. This proves the harness can detect transferable outcome-driven ranking change; it is deliberately **not** presented as a Habitus result.

## Per-category snapshot

| category         |   bm25 |   dense_lsa |   hybrid_rrf |
|:-----------------|-------:|------------:|-------------:|
| conflict         |  1     |       0.333 |        1     |
| exact            |  1     |       0.833 |        1     |
| multihop         |  1     |       1     |        1     |
| negative         |  0     |       0.5   |        0     |
| procedure        |  0.8   |       0.9   |        0.867 |
| protocol         |  1     |       1     |        1     |
| scope            |  1     |       1     |        1     |
| semantic         |  1     |       1     |        1     |
| temporal_asof    |  0.5   |       0.5   |        0.5   |
| temporal_current |  0.562 |       0.688 |        0.55  |

## Sandbox limitation

This environment cannot resolve outbound package/repository hosts from the coding container, so the real third-party packages/services could not be installed here. Their adapters and eligibility rules are included in the repository, but the result table marks them unavailable/ineligible rather than substituting simulations.
