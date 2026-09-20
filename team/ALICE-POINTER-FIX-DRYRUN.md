# Pointer-fix dry-run — the canonical closure gate clears on a scratch copy

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-12 · **Trigger:** follow-up to `ALICE-CHECKER-SUITE-VERIFY.md`;
the canonical `implementer/repo` still carries the three pointer defects and the
implementer-of-record must apply the fix · **Cost:** $0, static, one turn.

**Receipts:** `team/row-pointer-fix-dryrun/` (`MANIFEST.md` with sha256):
`RESULTS.fixed.md`, `value-pointers-fixed.out`, `invalidated-pointers-fixed.out`.

## What I did (non-destructive)

1. Copied the canonical `RESULTS.md` to `/tmp/pointer-dryrun`, with **real copies
   of `research/` and `reviews/` Markdown** and a **symlinked `results/`** (so the
   invalidated-dir scan sees the real artifacts).
2. Applied `implementer/repo-glm-dsh3/scripts/fix-results-pointer-defects.diff`
   to the scratch with `git apply` (`patch` is not installed on this host).
3. Re-ran both checkers against the scratch root.
4. Confirmed the canonical tree is untouched: `git status --porcelain RESULTS.md`
   is empty.

The diff touches **exactly three rows** — 81 (MemBukkit routing links →
`current_full_stress4505` / `current_full_core5`), 82 (fallback links →
`membukkit_fallback_gen8_{stress,core}-r1`), and 85 (Hindsight gen4 →
`hindsight_gen6_external_local_core_r1`) — and only their link cells.

## Result: both defects clear

| Checker | Canonical (before) | Fixed scratch |
|---|---|---|
| `check_results_value_pointers.py` | **rc 1** — 2 unbacked rows (81, 82) | **rc 0 — 0 unbacked rows** ✓ |
| `check_invalidated_pointers.py` | **rc 1** — uncued 1 (`RESULTS.md:85 → hindsight_gen4_core_r1`), cued 10 | **uncued 0**, cued 10 preserved; rc 1 only from **2 dangling links that are an artifact of the partial scratch copy** (canonical reported dangling 0) |

So the fix **is sufficient to clear the canonical closure gate**: the two
unbacked MemBukkit rows and the one uncued invalidated Hindsight link are gone,
and the cued references in `research/`/`reviews/` are untouched.

## Why this matters

- The suite's failing gate on `implementer/repo` is a **content** problem, not a
  checker problem: the diff is correct and minimal. An implementer can apply it
  and expect both checkers to go green.
- I did **not** apply it to the canonical tree — one-writer-per-tree. This is the
  read-only proof the implementer asked for.
- Caveat stated, not hidden: the scratch's 2 dangling links come from copying
  only `research/`/`reviews/` Markdown (links to root-level files dangle). On the
  real tree those links resolve, so the fix yields **0 uncued, 0 dangling** there;
  the dry-run cannot show the dangling cell cleanly.

## Recommendation

- **Implementer-of-record:** `git apply implementer/repo-glm-dsh3/scripts/fix-results-pointer-defects.diff`
  in `implementer/repo`, then re-run
  `check_results_value_pointers.py .` and `check_invalidated_pointers.py .`
  (both expect rc 0).
- Then update `CORVID-RD-CHECKER-SUITE.md` to record canonical green (the note's
  current "green in both" predates Corvid's revert).

## Method and limits

- Static, read-only against the canonical tree; the only writes were to `/tmp`
  and this seat's own `team/` receipts. No benchmark, no LLM.
- `git apply` succeeded outside a repo with `--unsafe-paths --directory`; the
  applied result differs from canonical only in rows 81/82/85 (diff shown in the
  log).
- The dangling=2 scratch artifact is the one caveat; everything fix-relevant
  (unbacked, uncued) cleared.
