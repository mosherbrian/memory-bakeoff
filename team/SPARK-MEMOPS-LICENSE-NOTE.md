# muse-drafter: MemOps code/data artifact located + license (spark pulse 2026-09-14)

Closes card residual (`CANDIDATE-CARD-MEMOPS.md`: "code/data not located in this pass").

- Code located: **`MemTensor/MemOps`** (created 2026-07-13, 15 commits, 6 stars) — paper itself links it (arXiv HTML: "Github https://github.com/MemTensor/MemOps"). **MIT license** (repo metadata + README badge). Do not confuse with `kedarvartak/MemOps` (unrelated observability layer).
- Design (repo overview, not imported): lifecycle-ops benchmark — Remember / Forget / Update / Reflect / TrajectoryOps, each sample with confirmed + tentative + retracted operations; gold operation traces point to exact user-turn spans; adjacent (clean) vs longitudinal (distractor-heavy) matched settings; templates in `template/` make the recipe auditable.
- Data lane: generation-and-evaluation framework — benchmark data is *generated* by the numbered pipeline, not a separate corpus download; no separate dataset terms surfaced. Treat data as repo-licensed (MIT) unless a release states otherwise.
- Grounding note for the card: lifecycle framing (create/supersede/forget/infer/revisit + provenance-to-turn-spans) is the closest published shape to our G1/G2 + provenance discipline; failure taxonomy (recency traps, update chains, stale distractors) overlaps our null/corpus concerns. Still candidate discovery only, no score import.
- P1 consequence: code lane green (MIT); data lane = generate-it-yourself (no third-party corpus terms). No score import.

$0, web reads only (search + repo metadata + paper HTML), no Muse batching. — muse-drafter (Spark)
