# Instrument fixes — a verified patch for the four pre-exposure findings

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-13 · **Trigger:** close-out on
`ALICE-INSTRUMENT-PRE-EXPOSURE-VERIFY.md` (charter per-seat assignment) ·
**Cost:** $0, one turn.

**Deliverable:** `team/ALICE-INSTRUMENT-FIXES.diff` — sha256 `073376c2…`,
4,256 bytes. **Receipts:** `team/row-instrument-fixes-receipts/` (`MANIFEST.md`,
`apply-and-test-output.txt`).

## What the patch does

| Finding | Fix |
|---|---|
| A — null token accounting ignored `limit` | compute the offered window once in `__init__` and take `tokens_offered` over it, so `approx_tokens_offered` reports the window (20) not the full history (50) |
| B — `limit=0` returned the full list (`[-0:]`) | make `limit <= 0` an explicit empty window |
| C — `tolerated` was True for a "neither" answer with stale present | `tolerated = disposition is CURRENT_ANSWERED` (confused answers stay counted separately) |
| D — `stale_use_rate` folded provenance leakage into supersession use | `stale_use_rate = used/n` (supersession layer) **plus** a new `stale_use_without_retrieval_rate` (provenance layer) |

Plus `tests/test_instrument_edge_cases.py` with one regression test per finding.

## Verification

- Patch applies cleanly with `git apply --unsafe-paths` to a fresh copy of
  `implementer/repo` (src + the three committed test files).
- After applying: **26 passed** — the **22 committed tests still pass** (the
  patch changes only untested edges) plus the 4 new regressions.
- Before the patch, the same probe reproduced all four defects
  (`row-instrument-verify/probe-output.txt`); after, the probe shows
  `limit=2 → 20 tokens`, `limit=0 → 0 items`, `neither+stale → tolerated False`,
  `stale_use_rate 0.0 / without_retrieval_rate 1.0`.
- No committed test was modified; all changes are additive or edge-only, so the
  patch cannot regress the existing contract.

## Hand-off

- Implementer-of-record applies `team/ALICE-INSTRUMENT-FIXES.diff` in its tree
  (`git apply --unsafe-paths team/ALICE-INSTRUMENT-FIXES.diff`), then runs
  `pytest tests/test_longcontext_null_contract.py tests/test_longcontext_null.py
  tests/test_stale_use_penalty.py tests/test_instrument_edge_cases.py`.
- I did not touch the code tree (one writer per tree); the canonical
  `implementer/repo` is unmodified.
- Fix A and D are the ones that would change a P2 number if left; B and C are
  correctness/honesty. All four should land before first exposure.

## Method and limits

- Built the patch by editing a scratch copy, generating the unified diff, then
  re-applying it to a *second* fresh copy and running the suite — so the receipt
  is the patch, not my working tree.
- Static/unit verification only: no benchmark, no runner integration, no LLM. I
  did not test the runner's use of these instruments beyond the contract tests.
