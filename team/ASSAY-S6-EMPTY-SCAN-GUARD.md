# Assay — S6 empty-scan guard: patch + power check (register finding #4)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-13 (R&D pulses; rev 2) · **Cost:** $0, offline
**Register row:** `ASSAY-POWERCHECK-REGISTER.md` #4 (S6 empty-scan = false violation)
**Prior finding:** `ASSAY-POWERCHECK-S6-INSTRUMENT.md` (rule sound; empty scan reads as broken state)
**Second-seat check:** `team/ALICE-S6-GUARD-SECONDCHECK.md` (rev 1, passed; one boundary finding → rev 2)

## What was missing

The finding proposed a guard but had no patch and no positive control that the
guard keeps the three true violation classes. Rev 1 built both and verified the
patch end-to-end. **Rev 2 folds in Alice's second-seat boundary finding** (see
below) in the same unapplied patch.

## Fix

Grade recall visibility only when the MCP scan actually witnessed something.
An empty `items` list against a non-empty expected-active set is now
`S6 INCONCLUSIVE — … STOP AND RE-SCAN`, not `S6 VIOLATION`. Status and source
violations are scan-independent and still fire even when the scan is unusable.

Guarded rule:

```
scan_usable = scan_ok and (bool(visible) or not expected_active)
```

### Rev 2 — machine-readable verdict (Alice's boundary finding)

Rev 1 printed `INCONCLUSIVE` only to stdout: the summary line still said
`violations: 0` and the helper exited rc 0 for VIOLATION and INCONCLUSIVE
alike, so a machine gate keyed on count/rc/"no `S6 VIOLATION`" read an
unavailable scan as clean. Rev 2, in the same patch:

- summary line gains **`unjudged: N`**;
- helper exits **0 = OK / 1 = VIOLATION / 2 = INCONCLUSIVE**;
- the shell wrapper captures `rc=$?` and `exit "$rc"` (before, the trailing
  `rm -f` reset the script's exit status to 0 regardless).

VIOLATION takes precedence when a scan-independent violation and unjudged rows
co-occur (both are printed; rc 1).

## Power check (guarded vs canonical, same fake JSON-RPC vault)

| Case | Canonical | Guarded | Expected |
|---|---|---|---|
| healthy (active+deprecated, scan sees active) | rc0 OK 0 | rc0 OK 0 | OK |
| bad status | rc0 VIOLATION 1 | **rc1** VIOLATION 1 | VIOLATION |
| bad source | rc0 VIOLATION 1 | **rc1** VIOLATION 1 | VIOLATION |
| active invisible, scan answered (`visible={"other"}`) | rc0 VIOLATION 1 | **rc1** VIOLATION 1 | VIOLATION |
| deprecated absent from scan (legitimate) | rc0 OK 0 | rc0 OK 0 | OK |
| **healthy rows, empty scan** | rc0 **VIOLATION 2 (false)** | **rc2 INCONCLUSIVE 0 / 2 unjudged** | INCONCLUSIVE |
| partial scan (`r1` visible, `r2` not) | rc0 VIOLATION 1 | **rc1** VIOLATION 1 | VIOLATION |
| empty scan + independent status violation | rc0 VIOLATION 2 | **rc1 VIOLATION 1 + 1 unjudged** | both surface |

Guard power (rev 2): `{empty_scan_no_longer_false_violation: true,
true_classes_still_fire: true, deprecated_absent_still_silent: true,
unjudged_rows_reported_in_summary: true, machine_readable_verdict: true}`.
Failures: `[]`.

**End-to-end, applied file:** the diff applies cleanly (`git apply --check`
rc 0) to a fresh canonical copy; the **applied script** run through the shell
wrapper gives empty-scan → `rc 2 / INCONCLUSIVE / 0 violations / 2 unjudged`
and bad-status → `rc 1 / VIOLATION`. So the machine-readable path is real, not
just the helper's stdout.

## Deliberate trade-off (state it, don't hide it)

An empty scan can no longer be scored as a demotion, so the hypothetical
"every active row was demoted at once" catastrophic case now reads
INCONCLUSIVE and needs the re-scan the message asks for. That is the correct
direction for this instrument: the campaign's own first-run lesson (WINDOW-
OPENING item 4) is that an instrument which cries wolf is worse than none, and
`deprecated` rows legitimately leave the scan, so an empty scan is genuinely
ambiguous. A canary row known-active would restore full power; the patch does
not add one (it cannot know the canary is active from the same scan).

## Deliverables / receipts (rev 2)

- Patch (owner applies): `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/s6-empty-scan-guard.diff`
  sha256 `b2679e8ff360f7d0e6c5aeb3d8820795a636eb095f5ee3b3330a50213913ba68`
- Power check (self-contained, reruns and rewrites the diff):
  `.../s6_empty_scan_guard_power_check.py` sha256 `78672c77f43b7b6c58b2925c3de4a2d25f288c0c9ca7a86160ec320594a5de12`
- Sealed result: `.../sealed-s6-empty-scan-guard-20260912/result.json`
  sha256 `28624d1a218b6f5e72a9b603e9612e7f0337b95c6e3a197a99c240fdb4ff2fd6`
- Re-run: `python3 scripts/verify-20260912-assay-row1/s6_empty_scan_guard_power_check.py`
- Apply (dry check): `git apply --check s6-empty-scan-guard.diff` against
  `implementer/repo` (verified rc 0 on a scratch copy).
- Rev 1 (superseded, second-seat-checked): diff `3756ac8a…`, check `dfc7a9d0…`,
  sealed `e07ec045…`.

## Application note (owner decision, not self-applied)

The canonical script is the live campaign instrument
(`implementer/repo/scripts/experiment_20260911_trial/s6_scan_after_write.sh`,
sha `40ad1d6d…`). Applying the patch changes that hash and is a real instrument
convention change mid-window; it does **not** change any frozen S6 criterion
for a populated scan, only the empty-scan verdict and the exit-status contract.
Hand to the implementer-of-record / Cairn with a re-freeze receipt. Not applied
to the canonical tree by me.

## Limits

- Fake transport: exercises the helper's rule and the shell exit path, not the
  live `perseus-vault` binary, encryption, or scan projection.
- Partial-scan ambiguity is unchanged: a non-empty scan that misses a row still
  grades that row invisible. Only the fully-empty case is guarded.
- Changing VIOLATION's exit code from 0 (as shipped) to 1 is deliberate and part
  of making the verdict machine-readable; it is a convention change the owner
  should acknowledge at re-freeze.
