# muse-drafter: MemoryArena data-license conflict resolved + follow-on use (spark pulse 2026-09-14)

The fan-out grounding passes disagreed on MemoryArena's data lane
(`SPARK-FANOUT-GROUNDING-CLOSURE-20260914.md`: "no HF dataset found" vs
`SPARK-FANOUT-LICENSE-PASS-20260914.md`: "HF data CC-BY-4.0"). Primary read
settles it. Candidate discovery only — **no score import**.

## Resolution

- HF dataset **`ZexueHe/memoryarena` exists** and is **CC-BY-4.0** (card states it
  outright). My earlier "no HF dataset linked" was **wrong** — the *paper* points
  to `memoryarena.github.io`, but the data lives on the first author's HF
  account. The parallel pass was right; conflict closed.
- Shape: 5 subsets (`bundled_shopping` 150 rows, plus `progressive_search`,
  `group_travel_planner`, `formal_reasoning_math`, `formal_reasoning_phys`),
  <1K rows, fields `id` / `questions` / `answers` / `backgrounds`.
- **Lane status: data CC-BY-4.0 (reuse-green), code repo `ZexueHe/MemoryArena`
  still has no LICENSE file (all-rights-reserved).** So MemoryArena is
  data-reusable but code-caution — the inverse of a normal "MIT code, restrict
  data" benchmark. Related data `ai-hyz/MemoryArena-product-db` also noted.

## New: an independent, controlled use of MemoryArena

`arXiv:2608.13883` — **"MemoryLake on MemoryArena: A Matched Study of Agent
Memory Backends."** Compares MemoryLake, Mem0, text-embedding-3-small vector RAG,
and a long-context control across all five MemoryArena domains, sharing the same
agent framework, model alias, task samples, and scoring code, with the **memory
integration the intentionally changed component**. It self-describes as a
**system-level matched comparison, not a representation-only ablation or a
cost-matched experiment** — the honest caveat to carry if cited. Relevance: a
third-party benchmark *use* of MemoryArena and another data point for the
MemDelta controlled-baseline thread (keep the caveat; it is engine-authored, so
vendor caution applies).

## Limits

Primary-read for the HF license + dataset shape; MemoryLake is abstract-level,
no numbers imported. Second seat: Alice.

$0, web reads only, no Muse batching. — muse-drafter (Spark)
