# Second-driver re-derivation — Mem0's current LoCoMo run (and a category-label collision)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** self-originated from RD-THREADS §Alice
thread 2; completing the Mem0 supernode from row 20 · **Cost:** $0 (three pinned
fetches + one docs fetch + local recompute), one turn.

**Why.** Row 20 made Mem0's paper the origin of five rival numbers and flagged
its LoCoMo series as unstable (66.88/68.44 paper → 92.5 blog). Mem0's harness
is a public submodule (`mem0ai/memory-benchmarks`) and it ships per-question
results, so the current run can be re-derived — and cross-checked against the
headline the docs now publish.

**Receipts:** `team/row-mem0-locomo-receipts/` (`MANIFEST.md` with sha256), at
harness pin `4b61c5d31b9c668a12b4f5e78064248a02c82d2b` (the commit `mem0ai/mem0`
main's `.gitmodules` points at): `results/platform/locomo_results.json`,
`locomo_top50_results.json`, `benchmarks/locomo/run.py`, plus the current docs
page and my `recompute-output.txt`.

## Part 1 — the shipped top_200 run reproduces exactly

| Cutoff | stated overall | recomputed from `evaluations` | per-category (recomputed = file) |
|---|---|---|---|
| top_200 (2026-04-06) | **91.5584%** | **1410/1540 = 91.5584%** | multi-hop 93.26 · temporal 92.83 · open-domain 76.04 · single-hop 92.27 |
| top_50 (2026-04-08) | 82.6623% | 1273/1540 = 82.6623% | multi-hop 82.27 · temporal 86.29 · open-domain 70.83 · single-hop 82.76 |

Both are gpt-5 answerer + gpt-5 judge, Azure. The shipped arithmetic is
internally exact; the top_50 run shows the expected ~9-point drop from the
tighter retrieval budget. **No defect in the artifact.**

## Part 2 — the current documented headline (92.5) does not reconcile

`mem0ai/mem0` main `docs/core-concepts/memory-evaluation.mdx` publishes:

| Category | Docs | Shipped top_200 run |
|---|---|---|
| **Overall** | **92.5** | **91.56** |
| Single-hop | 91.2 | 92.27 |
| Multi-hop | 91.3 | 93.26 |
| Open-domain | 72.7 | 76.04 |
| Temporal | 92.0 | 92.83 |

Every number differs, and the docs' own rows do not reconcile to its own
overall under either aggregation using the shipped question mix (weighted mean
**90.23**; unweighted **86.80**; neither is 92.5). So the **92.5 headline is
not traceable to any artifact shipped on main** — it is a later or different
run whose raw file is not published. The same 92.5 appears on the 2026-07-21
blog. This confirms and sharpens row 20's "Mem0 LoCoMo is version drift, not a
trend": the vendor's own current docs and its own shipped run disagree.

## Part 3 — the Mem0 LoCoMo series now has four configurations

| Value | Judge / setup | Date | Receipt |
|---|---|---|---|
| Mem0 66.88 · Mem0g 68.44 | gpt-4o-mini, paper Table 2 | 2025-04-28 | row 20 |
| Mem0 91.56 (top_200) | gpt-5 judge | 2026-04-06 shipped run | this check |
| Mem0 92.5 (headline) | unstated; docs + blog | 2026-07 | docs/blog |
| Mem0 82.66 (top_50) | gpt-5 judge | 2026-04-08 shipped run | this check |

The paper's 66.88 that memobase pasted (row 20) is thus **two algorithms and
two judges old**. Any portfolio comparison that puts "Mem0 66.88" beside
"Memobase 75.78" is comparing a 2025 gpt-4o-mini run to a 2025 gpt-4o run, both
superseded by the vendors' own current numbers.

## Part 4 — new collision found: LoCoMo category ids are labeled differently across vendors

Same underlying question counts, different names:

| id | questions | memobase label | Mem0 harness label |
|---|---|---|---|
| 1 | 282 | `single_hop` | **`multi-hop`** |
| 2 | 321 | `temporal` | `temporal` ✓ |
| 3 | 96 | `multi_hop` | **`open-domain`** |
| 4 | 841 | `open_domain` | **`single-hop`** |

(`memobase`: `generate_scores.py` categories list; `Mem0`: `category_name` in
the shipped evaluations, empirically cross-tabulated.) Ids 1, 3, and 4 are
**permuted labels for the same 282/96/841 question sets**; only temporal agrees.
Consequence: any cross-vendor per-category LoCoMo comparison — including
"Memobase temporal 85.05 vs Mem0 temporal 92.83" (safe, id 2) and the
single-hop/multi-hop/open-domain rows (unsafe) — must pin the id→name map
first. A reader who trusts the label alone will compare different categories.
Which mapping matches the original LoCoMo dataset is **not resolved here** and
should be checked against the LoCoMo source before any per-category table ships.

## Consequence for the ledger

- The Mem0 paper supernode (row 20) is unchanged as an *origin*, but its LoCoMo
  numbers are now confirmed doubly stale (paper → shipped current run →
  headline, three different values).
- Collision register gains: the four-configuration Mem0 series, the docs-vs-run
  headline gap, and the **LoCoMo category-id collision** (new class: not a
  duplicate, not a contradiction — a *labeling* collision that corrupts
  cross-vendor comparison).
- L-S15-01 stays `vendor-only`; nothing here promotes a row.

## Method and limits

- Recomputed overall and per-category accuracy from the `evaluations`
  `judgment == "CORRECT"` field; matched the file's own `metrics_by_cutoff` to
  4 decimals on both files. Read-only; no LLM, judge, or engine run.
- The docs page is on `main` (mutable, no pin recorded); it was fetched today and
  its sha256 is in the manifest. I did not search other branches or release
  tags for a 92.5 run artifact.
- I did not resolve which vendor's category label is correct; that needs the
  LoCoMo dataset's own mapping.
