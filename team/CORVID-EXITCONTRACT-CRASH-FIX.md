# Corvid R&D pulse — exit-contract meta-guard v2 (closes Alice's crash power-finding)

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity seat
**Date:** 2026-09-13 08:42 UTC · **Cost:** $0, local, no LLM, no network
**Trigger:** Alice's second-seat power check of Muse 4.1
(`team/ALICE-EXITCONTRACT-METAGUARD-CHECK.md`, sha `18eba0db…`) found that the
dirty control asserted only an exit code, so a checker that **crashes** on dirty
input reads as a detection. This closes that finding and the unimplemented
"structured verdict" half of Muse 4.1.

## What changed

`repo-glm-dsh3/scripts/check_checker_exit_contracts.py`
sha256 `9d6d27fe…` → **`fa579cc7…`** (single file; untracked, uncommitted).

`evaluate()` now enforces three things per guard, not one:

| Control | Before | v2 |
|---|---|---|
| clean fixture | rc == 0 | rc == 0 **and no Python traceback** |
| dirty fixture | rc == 1 | rc == 1 **and no Python traceback** **and** output matches the guard's own finding marker |

The nine markers are declared in the `_build_checks()` table, e.g.
`\[(?:UNCUED\|DANGLING)\]`, `non-canonical=[1-9]`, `FORK `, `\[DRIFT\]`. The
marker is part of the contract on purpose: editing a guard's summary wording
without updating the table is now a visible contract change, not a silent
no-op.

## Verification

- `--self-test` **PASS**, now exercising four synthetic contract classes:
  1. correct checker (clean 0 / dirty 1 + marker) — no false alarm;
  2. prose-only, exits 0 on dirty — caught (`exit 0`);
  3. **crashy** (clean 0, dirty uncaught `RuntimeError`) — caught
     (`exit 1 but output is a crash traceback, not a verdict`) — the exact case
     Alice demonstrated;
  4. finding-less exit-1 checker — caught (`exit 1 without the finding
     marker`).
- Full run on today's real guard set: **9/9 contracts hold**, exit 0. The new
  traceback + marker assertions do not false-alarm on any real guard.
- This is the guard's real decision path (`evaluate` driven directly in the
  self-test), not a re-implementation. No other file changed; no tree modified
  except this one script.

## Handoff

- Second-seat re-check open for Alice: re-hash `a09286ee…` (rev 3; see the Rev 3
  section), re-run `--self-test` and the full driver, and re-run her own
  crashy/always1/detector/wolfer cases through the new `evaluate` (she already
  has the harness).
- `team/CORVID-RD-CHECKER-SUITE.md` receipt row updated to `a09286ee…`
  (10th guard).
- Still not committed; `repo-glm-dsh3` remains the owner's worktree.

## Limits

- I did not force a real guard to crash; the crash path is covered by the
  synthetic self-test case, which is the only place it can be produced without
  editing a guard.
- The marker regexes are tied to each guard's current summary wording. That is
  intentional coupling, but it means a future wording edit must update this
  table or the full run will flag it.

## Rev 3 (2026-09-13 08:58 UTC) — closes Alice's clean-marker-absence finding

Alice's 08:49 re-check PASSed rev 2 and found one latent boundary: the clean
control asserted rc 0 + no traceback but not marker *absence*, so a checker that
prints its finding on every run ("cries wolf") would pass; live exposure 0/9.
Fixed in the same file: the clean control now also fails if the finding marker
appears on the clean fixture. `--self-test` gains a `wolfer.py` case (prints the
marker on every run) and now covers **five** synthetic contract classes:
correct, prose-only/exit-0, crashy, finding-less exit-1, clean-root marker-crier.
Re-run: self-test PASS, real set still **9/9 hold**, exit 0.
sha `fa579cc7…` → **`a09286ee…`**; suite receipt row updated. Second-seat
re-check open for Alice (rev 3).
