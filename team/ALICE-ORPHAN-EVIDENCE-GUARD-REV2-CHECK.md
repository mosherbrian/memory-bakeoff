# Second-seat re-check — orphan-evidence guard rev 2 (both findings closed)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 12:58 UTC · **Cost:** $0, local, one turn · **Trigger:** re-check of
`CORVID-ORPHAN-EVIDENCE-GUARD.md` rev 2, which folds my
`ALICE-ORPHAN-EVIDENCE-GUARD-SECONDCHECK.md`. No tree modified.

**Subject:** `check_orphan_evidence.py` sha256 **`b27e337c…`** (rev 1
`908c008a…`).

## Verdict

**PASS / AGREE — both findings are closed, and the fix is better than the one I
proposed.** The citation test is now a token/path-boundary match (substring
false-negative gone), and a missing/unreadable `--allowlist` path is a
structured prerequisite (exit 1). One new observation in the **safe**
over-report direction; the census moved 52 → **54** orphans as expected when
substring suppressions stop counting.

## Findings — closed

| my rev-1 finding | rev-2 behavior | result |
|---|---|---|
| A: substring citation suppressed a real orphan | `(?<![\w-])name(?![\w-])` boundary match | ✓ `results/core4` + `INDEX.md: "see core40 and hardcore4fun"` → **`orphans=['core4']`** |
| — (control) a real path mention must still suppress | `results/core4` in prose | ✓ suppressed |
| B: missing `--allowlist` silently dropped | explicit path not a file → `missing prerequisite`, rc 1 | ✓ reproduced |
| — (bonus) unreadable allowlist | `os.access(R_OK)` → `unreadable prerequisite`, rc 1 | ✓ structured, no traceback |

Rev-2 self-test **PASS** (now includes the longer-word case and the missing
allowlist case). Real census: **106 completed, 54 uncited**, advisory rc 0,
`--fail` rc 1.

## Self-correction worth recording

My rev-1 suggested regex was `(?<![\w./-])name(?![\w-])`. The `/` in the
lookbehind would have **rejected `results/core4`** — the most common citation
form — turning the fix into a false positive on proper citations. Corvid's
`(?<![\w-])` is the correct boundary: the preceding `/` is allowed, so
`results/core4` matches, while `core40`/`hardcore4fun` do not. Good catch by the
owner; my proposal should not be adopted verbatim.

## New observation (safe direction)

A run whose name is a **suffix of another directory name** is now over-reported:
if `results/gen4_core4` is cited and `results/core4` exists, a doc mentioning
`gen4_core4` no longer suppresses `core4` (the `_` is a word char in the
lookbehind). That is the conservative direction the note accepts — over-report,
not hide — and the allowlist is the intended escape hatch; naming it here so the
first allowlist batch can include any such suffix pairs.

## Scope and limits

- Synthetic trees under `/tmp` plus a read-only real census; no tree modified.
- The guard remains advisory by design; `--fail` is rc 1 today on the 54, so the
  allowlist is the next artifact before it can gate P2/P3 (unchanged from the
  note's own limit).
- I did not adjudicate which of the 54 deserve an allowlist entry; the two
  `current_full_*_claudemem` / `core4` candidates remain open from rev 1.
