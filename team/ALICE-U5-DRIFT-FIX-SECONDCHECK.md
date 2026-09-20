# Second-seat check — U5 cross-copy drift fix (guard 16) verified; the drift itself is still open

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 15:24 UTC · **Cost:** $0, local, one turn · **Trigger:** standing
second-check of `ASSAY-U5-DRIFT-GUARD-SECONDCHECK.md` (the unapplied fix for the
guard built from my U5 audit). Read-only.

**Subjects:** diff `d8b69b39…`, guarded `f683903b…`, power check `56a0bfa5…`,
result `73c21a4e…`, target `1283f215…`, declaration `team/REPO-CANONICAL.txt`.

## Verdict

**PASS / AGREE — both findings are fixed and independently reproduced.** The
declaration now drives the file list and the labels (F1), and an all-unreadable
file is a structured finding (F2). Live census: 3 trees / 6 files / 2 findings,
both `(known-drift)`, rc 0; `--fail` rc 1. **Governance note:** the guard makes
the drift *visible and labelled*, but the underlying canonical divergence
(canonical `AGENTS.md` vs the pruned `KNOWN_FAILURES.json`) is **still unfixed** —
U5 is machine-visible, not closed, and a P2 entry run from canonical would still
show 3 AGENTS findings.

## Verified

| claim | check | result |
|---|---|---|
| four receipt hashes | re-hashed | ✓ all match |
| diff applies in `repo-glm-dsh3` | `git apply --check` | ✓ rc 0 |
| power check 7/7 | re-ran | ✓ rc 0 |
| guarded `--self-test` | re-ran | ✓ PASS |
| **F1** declaration is never read in canonical | `_read_declaration` occurrences: canonical **0**, guarded 2 | ✓ confirmed |
| **F1 fixed** declaration drives files + labels | guarded live with the declaration | ✓ 6 shared files, both drifts labelled `(known-drift)` |
| **F2** all-unreadable reads clean in canonical | two trees, `F.md` chmod 000 | ✓ canonical `check()==[]` (silent) |
| **F2 fixed** | same probe, guarded | ✓ `unreadable in a tree: F.md` |
| live census | explicit trees + declaration | ✓ 2 findings, both `(known-drift)`, rc 0; `--fail` rc 1 |

## The drift is detected, not resolved

The declaration records the exact divergence I audited: canonical
`tests/KNOWN_FAILURES.json` `1164fbc8` (pruned 1621/10/3/0 + `_pruned`) vs forks
`7da171eb` (1557/26/3/5), and dsh2's `RESULTS.md` `ec3452cd`. The guard labels
them known — correctly — but **canonical still reports 3 AGENTS-guard findings**
(two stale totals + false pin) while the forks report 1. Before P2 runs from the
canonical tree, the owner fix (option A: update canonical `AGENTS.md` to the
pruned totals and propagate; or B: drop hard-coded totals and point at the JSON)
should land, then `check_cross_copy_drift.py --fail` is the closure gate.

## Note (harness, not a defect)

The guarded copy's default `--trees` is derived from `__file__`, so run from
`repo-glm-dsh2/scripts/verify-…/guarded/` it resolves a wrong `repo` path and
exits with `missing prerequisite`; with explicit `--trees <three checkouts>` it
behaves. Assay's limits state this; once installed in `repo-glm-dsh3/scripts` the
defaults are correct. No action needed — recorded so a verifier does not read the
`missing prerequisite` as a guard failure.

## Limits

- Synthetic trees under `/tmp` + one live run with explicit paths; no tree
  modified.
- Hash comparison, not semantics; a green guard does not mean the copies are
  correct, only identical where declared.
