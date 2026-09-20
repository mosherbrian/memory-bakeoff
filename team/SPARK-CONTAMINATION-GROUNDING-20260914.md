# muse-drafter: contamination methodology grounding + what it means for our corpus (spark pulse 2026-09-14)

Closes fan-out #4 (`SPARK-CONTRADICTION-FANOUT-20260914.md`, design corner 5).
Abstract-level, **no score import**.

## Pins

| | Paper A | Paper B |
|---|---|---|
| Title | *Contamination Inflates Scores but Rarely Reorders Large Language Model Leaderboards* | *LLM Benchmark Datasets Should Be Contamination-Resistant* |
| Authors | Xingyao Xiao (Stanford), Yihong Cheng (City U. Macau) | Ali Al-Lawati, Jason Lucas, Dongwon Lee, Suhang Wang (Penn State) |
| ID / date | [`arXiv:2609.02899`](https://arxiv.org/abs/2609.02899) v1 2026-07-05, cs.CL/stat.AP/stat.ME | [`arXiv:2605.19999`](https://arxiv.org/abs/2605.19999) v1 2026-05-19, **ICML 2026 Position Paper Track** |
| Artifact | "Code and data" (URL given) | harness/method paper (latent-form release) |

## Paper A — the actionable finding

- Recasts contamination as **anchor-item invariance**: compare an item's
  differential functioning against a **semantically-equivalent paraphrase** held
  at fixed skill, so memorization is separated from capability.
- Calibrates against ground truth: recovers an injected contamination dose
  (+0.187 accuracy points for test-set leakage) and never flags a negative
  control (-0.012).
- Impact: the rank correlation between the standard and paraphrase-controlled
  leaderboards is **0.997**; only **3 of 188** model×benchmark cases show
  differential contamination corroborated across two references.
- Conclusion: contamination **inflates absolute scores but rarely reorders
  rankings**; reordering requires the rare **differential** case (contaminating
  some systems more than others), not uniform contamination.

## What it means for us (design corner 5, no run)

1. **Our absolute hit rates are the exposure; our rankings are likely robust.**
   If any of our corpus records sit in a model's training set, the *level* of an
   arm's score can inflate while the **ordering** of arms mostly survives. So a
   contamination worry should be answered with (a) a level caveat and (b) a
   per-arm contamination-exposure statement — **differential** exposure is the
   only thing that can reorder, and that is what we would have to test.
2. **A cheap local invariant exists.** Adapt anchor-item invariance: hold a small
   set of records, author a **semantically-equivalent paraphrase** of each
   (same skill, different surface), and check whether any arm's score moves
   differentially between original and paraphrase. A move that is not uniform
   across arms is evidence of memorization, not capability. This is a probe we
   could build without a new benchmark, and it reuses the marker-free discipline
   already required by the stale-path probe (paraphrase must not leak the key).
3. **Report per-arm exposure, not one global rate.** Paper A's whole point is
   that a single "X% contaminated" figure answers the wrong question; the
   reordering-relevant quantity is differential across systems.

Paper B (latent-form, contamination-resistant release) is largely **not
applicable** to us: we do not release a benchmark, and our corpus is private
transcripts. Its value is as a release-format reference only.

## Frontier-harvest status (all four fan-out-2 items dispositioned)

- #1 MemStrata → card-ready; artifact verified absent/vendor-affiliated.
- #2 break-even study → second cost datum; five-pin template proposed.
- #3 cross-scenario generality → design reference; corroborates MemoryArena gaps.
- #4 contamination pair → this note; feeds design corner 5 with a concrete probe.

Next natural step for this seat: **one consolidation register** of the frontier
harvest (cards + fan-out candidates + dispositions) so a cold reader or a
verifier has a single entry point instead of ~18 daily Spark notes.

$0, web-read pins + our docs, no Muse batching. — muse-drafter (Spark)
