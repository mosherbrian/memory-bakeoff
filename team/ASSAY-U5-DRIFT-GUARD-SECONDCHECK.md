# Assay second-seat — U5 cross-copy drift guard (16) + two findings

**Verifier:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, static
**Subject:** `implementer/repo-glm-dsh3/scripts/check_cross_copy_drift.py`
`1283f215…` (Corvid, U5 closure), per its handoff.
**Verdict: PASS on the guard's live behavior; two findings** (one real: the
declaration file is never read; one low: an all-unreadable file reads clean),
with a validated fix. **Owner: Corvid. Diff NOT applied.**

## Reproduced

- sha `1283f215…`; `--self-test` PASS.
- Live census over the three trees: **2 drifts**, exactly as declared —
  `tests/KNOWN_FAILURES.json` (canonical `1164fbc8` vs forks `7da171eb`) and
  `RESULTS.md` (`repo-glm-dsh2` `ec3452cd` vs canonical/dsh3 `abe0832f`);
  advisory **rc 0**, `--fail` **rc 1**.

## F1 (real) — `team/REPO-CANONICAL.txt` is never read

The guard's docstring says "the canonical tree and the shared list are declared
in `team/REPO-CANONICAL.txt`", but the code hardcodes
`DEFAULT_FILES = (AGENTS.md, tests/KNOWN_FAILURES.json, …)` and never opens the
declaration. Consequences:

- adding a `shared:` line to the declaration has **no effect** on the default run
  (a new shared file is not checked unless `--files` is passed manually);
- the `known-drift:` ownership lines are not consumed, so the declaration's
  promise that "a **NEW** drift stands out" is not automatic — the guard prints
  known and new drifts identically and a reader must diff against the file.

## F2 (low) — an all-unreadable shared file reads clean

`_hash` returns the **string** `"UNREADABLE"` on `OSError`, but `check` builds
`distinct = {h for h in hashes.values() if h is not None}`. If every tree's copy
is unreadable, `distinct == {"UNREADABLE"}` (one value) and `missing == []`, so
**no finding** — the same "unavailable reads as clean" class the suite closed
elsewhere. Probe: two trees, `F.md` chmod 000 in both → canonical `check() == []`.

## Patch (`u5-drift-declaration.diff`, sha `d8b69b39335c…`)

- `_read_declaration()` parses `shared:` files and `known-drift:` paths; when
  `--files` is omitted the declaration is the default file list, and a missing
  explicit declaration is a structured prerequisite;
- drift findings are labelled **`(known-drift)`** or **`(NEW)`**;
- `check()` reports **`unreadable in a tree: <rel>`** and excludes
  `"UNREADABLE"` from the drift set.

`git apply --check` clean in `implementer/repo-glm-dsh3`.

## Power check — 7/7

| case | canonical `1283f215` | guarded |
|---|---|---|
| `--self-test` | PASS | PASS |
| declaration drives files + labels | — | `KNOWN.md (known-drift)` + `NEW.md (NEW)`, rc 0 |
| declaration reader present | **no** | yes |
| all-unreadable file | **[] silent** | **`unreadable in a tree: F.md`** |
| live census | 2 unlabelled drifts | 2 **`(known-drift)`**, rc 0 |
| live `--fail` | rc 1 | rc 1 |
| missing declaration | (no such flag) | `missing prerequisite`, rc 1 |

## Limits

- F1's patch changes the default file source from the hardcoded tuple to the
  declaration; if the declaration is absent the hardcoded tuple still applies.
- `known-drift` is parsed by the first token after the colon; the remaining
  free-text owner/hash fields stay documentation.
- Static only; no tree modified.

## Receipts

- Diff: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-u5-drift-fix/u5-drift-declaration.diff`
  sha256 `d8b69b39335c…`
- Guarded guard: `.../guarded/check_cross_copy_drift.py` `f683903b057d…`
- Power check: `.../u5_drift_fix_power_check.py` `56a0bfa5120f…`
- Result: `.../result.json` `73c21a4ea383…`
- Target: `check_cross_copy_drift.py` `1283f215…`; declaration `team/REPO-CANONICAL.txt`

— **Assay** (`worker-glm-dsh2`). No tree modified.
