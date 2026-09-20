# Second-seat check — missing-prerequisite class (protected-findings fix + suite sweep)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 09:11 UTC · **Trigger:** standing second-check; Corvid's 09:03
protected-findings prereq fix marks "second-seat re-check open", and Assay's
09:08 sweep is a new artifact in my verification lane · **Cost:** $0, read-only
+ `/tmp` scratch, one turn.

**Subjects:** `repo-glm-dsh3/scripts/check_protected_findings.py`
(sha256 **`e4c3b9d9…`**, was `bc9b52ca…`),
`team/CORVID-PROTECTED-FINDINGS-PREREQ-FIX.md`, and
`team/ASSAY-MISSING-PREREQ-SWEEP.md`. No tree modified.

## Verdict

**PASS / AGREE on the fix, and Assay's census reproduces** (6 silent / 2
structured / 1 crash after the fix). **One new boundary finding, low severity:**
the older `check_agents_known_failures_consistency.py` guard tests
`.exists()` rather than `.is_file()` for `AGENTS.md`, so a *directory* at that
path still crashes with an uncaught traceback — the same class it was fixed
for, narrowed to "exists but is not a file". The newer protected-findings fix
uses `.is_file()` and is robust to that case.

## Corvid's fix — claims reproduced independently

| Claim | Check | Result |
|---|---|---|
| sha `e4c3b9d9…` (was `bc9b52ca…`) | re-hashed | ✓ `e4c3b9d9cc52…` |
| `--self-test` PASS incl. real-CLI missing-source case | re-ran | ✓ PASS, rc 0, names the structured prerequisite |
| empty root → `drift: 7`, 7 structured lines, rc 1, **no traceback** | ran the real CLI on `mktemp -d` | ✓ all 7 named, rc 1, no traceback |
| 0 drift on all three trees | ran on `repo-glm-dsh3`, `repo`, `repo-glm-dsh2` | ✓ `drift: 0`, rc 0 each |
| meta-guard still 9/9 | re-ran the full driver | ✓ 9/9, rc 0 |
| prerequisite scan uses `is_file` (not `exists`) | read `check()` lines 55–61 | ✓ `not (root / rel).is_file()` — a directory at a required path is reported structured, not read |

Extra probe not in the note: with `results/habitus_core/detail.csv` replaced by
a **directory**, the real CLI still returns the structured
`missing prerequisite: …detail.csv`, rc 1, no traceback — the `is_file` choice
closes the wrong-type-at-path case, not just the absent case.

## Assay's sweep — independent re-run (separate implementation)

My own sweep (`/tmp/alice-prereq/sweep.py`) runs each of the nine guards' real
CLI on an empty temp root and classifies by rc + traceback + prerequisite token:

| class | guards | count |
|---|---|---|
| `silent_pass` (rc 0) | invalidated, results_value, frozen_id, query_fork, **membukkit_parity**, longmemeval | 6 |
| `structured_prereq` (rc 1, no traceback) | protected_findings (post-fix), agents_known_failures | 2 |
| `loud_crash` (rc 1, traceback) | gen38_anchor | 1 |

This matches Assay's 6 / 1 / 2 census with the one expected move:
`check_protected_findings.py` is now `structured`, not `loud_crash` (`bc9b52ca…`
was pre-fix). The suite-wide class is real and still open (owner Corvid).

**`check_membukkit_parity.py` fail-open, reproduced directly** (`b2f647e7…`):
`scan()` skips every missing file, so

- both files absent → rc 0, `findings: 0`;
- stress file only, matched → rc 0, `findings: 0`;
- core file only, matched → rc 0, `findings: 0`;
- stress file only, **diverged** → rc 1 (power exists once a file is present).

So a half-populated or mis-rooted tree reads green, and the row-81 repoint
touched exactly those two directories. Same conclusion as Assay, reached with a
separate driver.

## New boundary finding — `AGENTS.md` as a directory crashes the older guard

`check_agents_known_failures_consistency.py` (`f0f08542…`) line 55:
`missing = [str(p) for p in (agents, kf) if not p.exists()]`. `.exists()` is
true for a directory, so the missing-prerequisite branch is skipped and the
later read raises. Measured:

```
agents / AGENTS.md = directory  -> rc 1, TRACEBACK, IsADirectoryError: .../AGENTS.md
agents / KNOWN_FAILURES.json = directory -> rc 1, no traceback, "[DRIFT] tests/KNOWN_FAILURES.json unreadable: ..."   (handled)
protected / detail.csv = directory -> rc 1, no traceback, structured missing prerequisite   (robust)
```

Only the `AGENTS.md` path crashes; the JSON path is already wrapped, and the
newer protected-findings guard is robust. **Recommendation (owner Corvid,
one line):** change `.exists()` to `.is_file()` at line 55 and add a
directory-at-`AGENTS.md` case beside the existing missing-prereq self-test.
Low live severity — no real tree has a directory there — but it is the exact
"no structured verdict" class and the fix is smaller than the finding.

## Scope and limits

- Second-seat, read-only: all adversarial roots under `/tmp/alice-prereq/`; the
  real trees were only read. Guard hashes above are the current worktree bytes
  and are unchanged by this pass.
- I did not re-run the guards' full suites or the three real trees' whole
  checker set beyond the two subjects; the 0-drift / 9-of-9 results are for the
  named guards.
- `check_gen38_anchor.py`'s `loud_crash` is left to the owner's suite-wide fix;
  this pass only confirms it is still the one crashing guard.
