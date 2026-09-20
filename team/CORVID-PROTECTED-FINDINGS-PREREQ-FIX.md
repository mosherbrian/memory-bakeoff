# FIX — `check_protected_findings.py` missing source is a verdict, not a traceback

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity seat
**Date:** 2026-09-13 09:03 UTC · **Cost:** $0, local, no LLM, no network
**Trigger:** Assay's 08:55 power check (`team/ASSAY-POWERCHECK-PROTECTED-FINDINGS.md`,
result sha `ac09f969…`): deleting a source makes the guard's real CLI exit 1 with
an uncaught `FileNotFoundError` instead of a structured verdict — the same
missing-prerequisite class already fixed in
`check_agents_known_failures_consistency.py`. Owner: Corvid.
**Consumer:** the exit-contract meta-guard / Alice's next second-seat pass.

## Change

`implementer/repo-glm-dsh3/scripts/check_protected_findings.py`
sha256 `bc9b52ca…` → **`e4c3b9d9…`** (one file; untracked in this lane).

- `check()` now begins with a prerequisite scan of the seven required artifacts
  (`lifecycle.json`, the three summary CSVs, `detail.csv`, `READER_FINDINGS.md`).
  Any absent path returns a structured finding
  `missing prerequisite: <relpath>` (`got: absent`, `want: present`) for **each**
  missing file, instead of proceeding into a read that raises.
- `--self-test` gains a real-CLI case on an empty root: it asserts rc 1, that the
  output contains `missing prerequisite: `, and that it contains **no**
  `Traceback (most recent call last)`. Assay correctly noted the meta-guard's
  dirty fixture mutates a *present* file, so this path is not exercised by the
  9/9 contract check; the self-test is now the control for it.
- Docstring records the behavior.

## Verification

- `--self-test` **PASS** (clean fixture; drifted habitus; 0.955 subset; missing
  source reported, not crashed).
- Real run: **0 drift** on all three trees
  (`repo-glm-dsh3`, canonical `implementer/repo`, `repo-glm-dsh2`).
- Empty root through the real CLI: `protected-finding drift: 7`, seven
  `missing prerequisite:` lines, **rc 1, no traceback**.
- Exit-contract meta-guard re-run: still **9/9 hold**, exit 0 (its
  protected-findings marker still matches the dirty fixture).

## Limits

- The guard remains a **static consistency** check: green means the artifacts
  still match the published protected numbers, not that those numbers are
  correct (they have separate second-driver receipts).
- The prerequisite list is exactly the seven files the guard reads; adding a
  protected finding means extending `REQUIRED` in the same edit.
