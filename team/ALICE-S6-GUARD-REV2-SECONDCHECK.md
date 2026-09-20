# Second-seat re-check — S6 empty-scan guard rev 2 (Assay register #4)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 · **Trigger:** rev 2 folds in my rev-1 boundary finding; Assay's log
says "second-seat re-check of rev2 is open" · **Cost:** $0, offline,
scratch-only, one turn. Supersedes the rev-1 verdict in
`team/ALICE-S6-GUARD-SECONDCHECK.md` only in artifact version, not in findings.

**Subject:** `team/ASSAY-S6-EMPTY-SCAN-GUARD.md` (rev 2) and the three receipts
it names. Assay's tree and the canonical tree were **not** modified.

## Verdict

**PASS — AGREE, no new finding.** Rev 2 correctly makes the verdict
machine-readable and reproduces end-to-end, including the applied shell
wrapper's exit status. My rev-1 boundary finding is closed.

## Checks

| # | Check | Result |
|---|---|---|
| 1 | rev-2 hashes: diff `b2679e8f…`, check `78672c77…`, sealed `28624d1a…` | ✓ all match the note |
| 2 | canonical base unchanged (`40ad1d6d…`, `implementer/repo`) | ✓ match |
| 3 | independent scratch re-run of the power check | ✓ exit 0; `guard_power` **5/5** true (incl. `unjudged_rows_reported_in_summary`, `machine_readable_verdict`); `failures: []`; 8/8 cases pass |
| 4 | per-case exit codes: true classes **rc1**, empty scan **rc2**, healthy/deprecated-absent **rc0** | ✓ as tabulated |
| 5 | regenerated diff vs committed diff | ✓ byte-identical, same sha |
| 6 | diff applies to a fresh canonical copy (`git apply`) | ✓ rc 0 |
| 7 | applied file == `build_guarded(canon)` text the power check exercised | ✓ exact equality |
| 8 | **applied shell wrapper** end-to-end (my run, not the helper) | ✓ empty → rc **2**, summary `violations: 0  unjudged: 2`, `S6 INCONCLUSIVE`; bad status → rc **1**, `S6 VIOLATION`; healthy → rc **0**, `S6 OK` |
| 9 | temp-helper hygiene after a nonzero run | ✓ no `/tmp/s6*.py` left behind (the wrapper's `rm -f` still runs) |

Checks 8–9 are the extra step beyond the committed power check, which drives
the Python helper directly. Running the **whole applied `.sh`** confirms the
`rc=$?` / `rm -f` / `exit "$rc"` wrapper path, and check 9 shows cleanup is not
lost on the new nonzero exits — true because the canonical script uses
`set -u`, **not** `set -e`, so a nonzero python return does not abort before
`rc=$?`. Had it been `set -e`, the wrapper would still have returned the right
status but leaked the helper; it does not.

## Notes for the re-freeze owner

- The exit-status contract (**0 OK / 1 VIOLATION / 2 INCONCLUSIVE**) is the
  machine interface now; the summary line's `unjudged: N` is the human/secondary
  signal. Both should travel with the re-freeze receipt, since rev 1 never had
  an exit contract and the campaign's consumers currently read stdout only.
- The VIOLATION case moves 0 → 1; Assay flags that as a deliberate convention
  change, and it is the right one (a catchable failure should not exit clean).
- No number, frozen S6 criterion for a populated scan, or result dir moved; the
  diff is a single-file instrument change, still unapplied to canonical.

## Method and limits

- Stored-artifact + offline re-derivation only: no live `perseus-vault` binary,
  encryption, scan projection, or live data; same fake-JSON-RPC transport as the
  original, so this validates the rule and the wrapper, not the live service.
- I did not apply the patch to canonical or to Assay's workspace; the runnable
  wrapper copy used for check 8 was a scratch copy with only the four hardcoded
  `BIN`/`DB`/`KEY`/`WS` assignments rewritten — helper and wrapper logic
  untouched, and the applied-vs-`build_guarded` equality in check 7 covers that
  the tested bytes are the patched bytes.
