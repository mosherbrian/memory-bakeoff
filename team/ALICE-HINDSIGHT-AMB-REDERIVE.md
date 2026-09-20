# Hindsight's marketed 94.6 / 92.0, re-derived — and why the report says 91.4

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** follow-up to
`ALICE-HINDSIGHT-THIRD-PARTY.md`; AMB links `vectorize-io/agent-memory-benchmark`,
which ships raw per-question outputs · **Cost:** $0 (three raw fetches + local
recompute; the two large files are hashed, not stored), one turn.

**Receipts:** `team/row-hindsight-amb-receipts/` (`MANIFEST.md` with sha256 for
small files; the two raw outputs are ~28 MB and ~54 MB gz — hash + size
recorded, re-fetchable, not copied).

## Result: the marketed numbers reproduce exactly

| Dataset | Source | Stated | Recomputed from per-question `correct` | Setup |
|---|---|---|---|---|
| LongMemEval-s | `outputs/longmemeval/hindsight/rag/s.json.gz` | 0.946 | **473/500 = 0.94600** | answerer `gemini-3.1-pro-preview`, judge `gemini-2.5-flash-lite` |
| LoCoMo10 | `outputs/locomo/locomo-hindsight/rag/locomo10.json.gz` | 0.9201 | **1417/1540 = 0.92013** | same answerer/judge |

The 2026 marketing **94.6% / 92.0%** are exactly the AMB harness runs, and the
raw per-question data is published. That is a real transparency plus: unlike
most vendors in this batch, Hindsight's marketed numbers are re-derivable.

## Why the report says 91.4

The 91.4-vs-94.6 gap is **run drift, not a contradiction**:

| Number | Where | Run |
|---|---|---|
| **91.4% LongMemEval / 89.61% LoCoMo** | Hindsight Technical Report abstract (`arXiv:2512.12818v1`, 2025-12-14) | the report's own run (models/judge unstated in the abstract) |
| **94.6% / 92.0%** | AMB harness + marketing page + blog (2026) | Gemini 3.1 Pro answerer + Gemini 2.5 Flash Lite judge, avg context 43.6k / 36.2k tokens |

The marketing page presents 94.6 as *the* number and contains no "91.4"; the
vendor's own report says 91.4. Two numbers, two runs — the collision register
should carry both.

## Two caveats the marketed number inherits

1. **Same-family judging.** The answerer (`gemini-3.1-pro-preview`) and judge
   (`gemini-2.5-flash-lite`) are both Google Gemini models. That is not
   self-grading (different models) but it is the same-family setup MemBukkit
   warns about, and the judge is a small/cheap model. Comparability depends on
   it, and it is not the official `gpt-4o` judge the LongMemEval paper ships.
2. **The marketing page's per-dimension breakdown does not match the shipped
   run.** The page lists Single-Session 96.2 · Cross-Session 93.8 · Temporal
   92.1 · Knowledge-Update 95.4 · Multi-Hop 95.1. The shipped LongMemEval run's
   per-`question_type` figures are: single-session-user **97.1** ·
   single-session-assistant **100.0** · single-session-preference **76.7** ·
   multi-session **91.0** · knowledge-update **97.4** · temporal **97.0**
   (no multi-hop type). The overall matches exactly; the breakdown does not
   reconcile under any obvious grouping. Flagged — possibly a different
   aggregation or run, not asserted as an error.

## Consequence for the ledger

- **Hindsight's marketed row upgrades to `vendor-only (independently
  recomputed from shipped raw rows)`** for the AMB 94.6/92.0 — the same upgrade
  Memobase and agentmemory got.
- The **report's 91.4** is a different, non-re-derivable run; the
  **"independent reproduction" is co-authorship** (previous artifact), so
  `third-party` stays empty.
- The transparency register's Hindsight row should be updated: it is not
  "self-attested only" — the *marketed AMB run* is re-derivable; the *report
  number* is not.

## Method and limits

- Recomputed `correct = count(results[].correct)` over 500 / 1,540 per-question
  records; matched the file's own `accuracy` to 6 dp. Read-only; no LLM, no
  re-run.
- The two raw files are large and were hashed rather than stored; the receipt
  records URL + bytes + sha256 so a re-verifier can re-fetch and diff.
- The per-dimension mismatch is reported as a discrepancy, not a proven error —
  I did not locate the aggregation that would reconcile it.
