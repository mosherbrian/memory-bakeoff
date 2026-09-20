# Candidate card — PrecisionMemBench (precision-aware retrieval benchmark)

**Author:** muse-drafter (proposal-drafter seat), Phase-B frontier harvest (Sprint-2 goal 5)
**Date:** 2026-09-14 · **Cost:** $0 (abstract-level + shipped-artifact reads)
**Status:** **candidate discovery only — no score import.** Fan-out candidate #3 of
5 (`SPARK-VOCABULARY-FANOUT-20260914.md`), handoff-ranked #3. Owner unassigned;
verifier: Alice. **Unusually strong receipts already exist** (below).

## Provenance

| Field | Value |
|---|---|
| Title | *Structured Belief State and the First Precision-Aware Benchmark for LLM Memory Retrieval* |
| Author | **Jeffrey Flynt** (single); product affiliation `tenurehq` |
| ID / date | [arXiv:2605.11325](https://arxiv.org/abs/2605.11325) v1 2026-05-11, **v4 2026-07-29**, cs.IR |
| Code | [`tenurehq/precisionMemBench`](https://github.com/tenurehq/precisionMemBench) — **MIT** (verified), committed per-case baseline reports |
| Data | HF [`tenurehq/precisionmembench`](https://huggingface.co/datasets/tenurehq/precisionmembench) — **MIT** (API-verified); HF Spaces leaderboard |
| Paper license | arXiv.org perpetual non-exclusive |
| Numbers | vendor-operated leaderboard; columns re-derived from shipped reports (see Verification) |

## What it is

- An **89-case benchmark** (77 single-turn + 12 turn-level session assertions)
  scoring retrieval by **required *and prohibited* belief IDs before generation** —
  i.e. precision/noise-isolation, not answer quality. Categories include alias
  resolution, scope disambiguation, **supersession chain exclusion**,
  cross-user isolation, budget eviction, counter-signal retrieval.
- A comparison leaderboard over ~13 providers (including `agentmemory`, `mem0`,
  `zep`, `hindsight`, `supermemory`, `a-mem`, `cognee`), run through thin FastAPI
  wrappers; only the operator's own system (`tenure`) is CI-reproduced.
- A structured belief-store method (Tenure) as the demonstrator.

## Map to our goals

| Goal | Fit | Notes |
|---|---|---|
| **E-3/E-4 retrieval precision** | **good** | "leakage is not recall" enforced by construction (prohibited IDs) |
| **G1/G2 (supersession exclusion)** | partial | a `supersession chain exclusion` category + counter-signal retrieval |
| **G5 scope isolation** | partial | cross-user isolation + scope disambiguation cases |
| serving cost | partial | reports retrieval p50/p95 and ingestion time |
| coding memory | weak | personal-assistant/belief store, not repositories |

## What it offers us

- A **required-AND-prohibited belief-ID scoring shape** — the cleanest external
  analogue of our harmful/prohibited-presence reporting, decoupled from generation.
- **A public, third-party measurement of our control arm `agentmemory`** (precision
  axis), which our portfolio otherwise only argues from lifecycle.

## What it cannot ground

Coding-memory results; and it is **vendor-operated** (the operator's system tops
the board). Its single-turn precision column is **diluted**: averaged over all
precision-bearing cases (nP 43–70 by provider), not the stated 43 active cases —
so the published 0.17 for `agentmemory` is 0.28 on the stated active set. Use it
as a **retrieval-precision method reference and a caveated cross-check**, never a
board to import.

## Next step (bounded)

None required for carding; the receipts below already exceed a discovery card. If
the security/precision arm adopts the required+prohibited shape, cite the
`agentmemory` snapshot explicitly as `agentmemory (npm 0.9.22, PMB 2026-05-29)`.

## Verification status (second-driver already done by this seat)

- **License**: repo **MIT**; HF dataset `tenurehq/precisionmembench` **MIT** (API-verified).
- **Session table re-derived clean** from the shipped per-turn reports (pass/rate/
  drift/precision/p50/p95; nearest-rank percentiles) —
  `SPARK-PMB-SESSION-REDERIVE-20260914.md` + `team/row-pmb-session/`.
- **Single-turn precision denominator finding** (stated 43 vs actual nP) —
  `SPARK-PMB-PRECISION-DENOMINATOR-20260914.md` + `team/row-pmb-precision/`.
- **`agentmemory` row identity/snapshot** (same project, different build) —
  `SPARK-PMB-AGENTMEMORY-IDENTITY-20260914.md`.
- All leaderboard numbers remain **vendor-operated claims — not citable**.
  Second seat: Alice (claim class).

— **muse-drafter** (Spark). Phase-B candidate discovery, $0; no score import.
