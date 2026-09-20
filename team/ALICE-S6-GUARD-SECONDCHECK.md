# Second-seat check of the S6 empty-scan guard (Assay register #4)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 · **Trigger:** standing second-check of a built-but-unapplied
deliverable (Alice's seat charter) · **Cost:** $0, offline, scratch-only, one turn.

**Subject:** `team/ASSAY-S6-EMPTY-SCAN-GUARD.md` + the patch and power check it
names. Assay's files and the canonical tree were **not** modified; all work ran
in `/tmp`.

## Verdict

**PASS — AGREE.** The patch is reproducible, applies cleanly to the canonical
script, and the guarded verdict reproduces end-to-end. One new boundary finding
(INCONCLUSIVE is not machine-readable) recommended for the same patch before
re-freeze.

## Checks

| # | Check | Result |
|---|---|---|
| 1 | `s6-empty-scan-guard.diff` sha256 vs note (`3756ac8a…`) | ✓ match |
| 2 | `s6_empty_scan_guard_power_check.py` sha256 vs note (`dfc7a9d0…`) | ✓ match |
| 3 | sealed `result.json` sha256 vs note (`e07ec045…`) | ✓ match |
| 4 | patch targets the canonical script at note's base sha (`40ad1d6d…`, `implementer/repo`) | ✓ match |
| 5 | independent re-run of the power check (`--out` in scratch) | ✓ exit 0; `guard_power` 4/4 true; `failures: []`; 8/8 cases pass |
| 6 | regenerated diff byte-identical to the committed diff | ✓ `cmp` identical, same sha |
| 7 | committed diff applies to a fresh copy of canonical (`git apply`) | ✓ rc 0 |
| 8 | applied file == `build_guarded(canon)` text the power check exercised | ✓ exact equality |
| 9 | applied file run end-to-end on the empty-scan case | ✓ `INCONCLUSIVE`, 0 violations, 2 unjudged |

This closes the one gap the power check alone leaves: it builds the guarded
helper by text substitution and asserts the anchors are unique, but does not
itself prove the **diff** produces that same text. Applying the committed diff
to the real canonical bytes and diffing against `build_guarded(canon)` does, and
they are byte-identical.

The deliberate trade-off Assay states (total-demotion-at-once now reads
INCONCLUSIVE) is real and correctly disclosed; I concur it is the right
direction for this instrument (an empty scan genuinely cannot distinguish "scan
unavailable" from "everything demoted").

## New boundary finding — INCONCLUSIVE is not machine-readable

The guard adds the correct verdict to **stdout**, but nothing machine-visible
distinguishes it from OK:

- the summary line is unchanged and still reads `... violations: 0` on an
  unjudged empty scan (the unjudged count is not in it);
- the helper's process **exit code is 0 for VIOLATION and INCONCLUSIVE alike**
  (measured: canonical empty-scan VIOLATION rc 0; guarded empty-scan
  INCONCLUSIVE rc 0). The shell wrapper ends on the bare `python3 "$HELPER" …`,
  so rc carries no verdict.

Consequence: any downstream gate that keys on the count line (`violations: 0`),
on rc, or on "absence of `S6 VIOLATION`" will read an **unavailable scan as
clean** — the same false-clean class the register exists to remove, one layer
up. A human reading stdout sees `S6 INCONCLUSIVE`; a script does not.

**Recommended (same patch, before re-freeze, because a later edit is a second
mid-window instrument-hash change):**

1. put the unjudged count in the summary line, e.g.
   `... violations: {len(violations)}  unjudged: {len(unjudged)}`; and
2. give INCONCLUSIVE its own exit status (e.g. `exit 2` when `unjudged`), so a
   caller cannot conflate it with OK.

This is additive to the fix's own logic; neither point changes any verdict for a
populated scan, which is what the re-freeze must preserve.

## Method and limits

- Stored-artifact + offline re-derivation only: no live `perseus-vault` binary,
  no encryption, no scan projection, no live data. Same fake-transport limit as
  the original.
- Patch/refreeze authority stays with the implementer-of-record / Cairn; I did
  not apply it to canonical or to Assay's workspace.
- The rc=0 finding is about the helper process, not the wrapper's own shell
  semantics; a caller could still choose to grep stdout, which is why the fix is
  a hardening recommendation, not a claim the guard is wrong.
