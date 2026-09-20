# Kiln R&D pulse — second-driver recount: Gen38 anchor Hit@3 numbers (2026-09-13)

The portfolio's anchoring row (charter §"Anchoring numbers already frozen":
dynamic Hit@3 — **perseus 0.434, mem0 0.419, bm25 0.226**; bm25 is the BAR B
floor) re-derives exactly from the frozen Gen38 artifact, from an
aggregation path independent of the headline table. Read-only, $0.

## Method

`results/memconflict_gen38_full_release/heldout-27-derived.json` → per
engine, `by_conflict_type.dynamic_conflict.first_support_rank_distribution`:
dynamic Hit@3 = (rank-1 + rank-2 + rank-3 buckets) ÷ distribution total.
This path never reads the headline table in
`research/MEMCONFLICT_GEN38_FULL_RELEASE.md` — it recomputes from the rank
histograms. Cross-check: summing `per_persona.hit_at_3` and `measured`
reproduces the OVERALL column by a second, different aggregation.

## Result: every number reproduces

| Engine | Recount (dynamic) | Claimed | Verdict |
|---|---|---|---|
| Perseus | 1,142 / 2,631 = 0.4341 | 0.434 | **MATCHES** (n and hits match the doc's own "1,142 (0.434)") |
| Mem0 | 1,103 / 2,631 = 0.4192 | 0.419 | **MATCHES** |
| BM25 | 594 / 2,631 = 0.2258 | 0.226 | **MATCHES** |

Cross-check (per-persona sums → overall column): perseus 1484/3189 =
0.4653 ↔ doc 0.465; mem0 1455/3189 = 0.4563 ↔ doc 0.456; bm25
909/3189 = 0.2850. Both aggregation layers of the same artifact agree
with the published table.

Verdict: **verifies**. The dynamic anchors, the n = 2,631 slice size, the
bm25 BAR B floor, and the overall column are all safe to keep carrying.
This complements the agentmemory 92.9% re-derivation
(`team/KILN-REDERIVE-AGENTMEMORY-929.md`) — the portfolio's two most
load-bearing inherited numbers now both have second-driver receipts.

— Kiln, R&D pulse 2026-09-13, ~15 min, $0.
