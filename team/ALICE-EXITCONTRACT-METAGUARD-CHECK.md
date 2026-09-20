# Second-seat / power check — checker exit-contract meta-guard (Muse 4.1)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 · **Trigger:** standing second-check of a new R&D artifact
(`check_checker_exit_contracts.py`, Muse batch 4 ACCEPT 4.1) · **Cost:** $0,
read-only + scratch, one turn.

**Subject:** `repo-glm-dsh3/scripts/check_checker_exit_contracts.py`
(sha256 `9d6d27fe…`), plus `team/MUSE-IDEATION-04.md` §Follow-up. No tree was
modified.

## Verdict

**PASS on the built guard** (hash, self-test, and 9/9 all reproduce). **One
power finding:** the dirty control asserts only an exit code, so a guard that
**crashes** on dirty input is counted as detecting it — and the
"machine-readable verdict" half of Muse 4.1's own minimal check is not
implemented.

## Verified claims

| Claim | Check | Result |
|---|---|---|
| sha `9d6d27fe…`; `--self-test` PASS | re-hashed; re-ran self-test | ✓ |
| 9/9 exit contracts hold | re-ran the full driver | ✓ 9/9, exit 0 (incl. the just-fixed AGENTS guard `f0f08542…`) |
| self-test proves it catches a checker that prints `FAIL` but exits 0 | read `_self_test` + ran it | ✓ that case is caught (`bad.py`) |
| fixtures drawn from each guard's own self-test recipe; three artifact guards reuse their `_fixture` | read `_build_checks` | ✓ |

## Finding — a crash on the dirty root passes as a detection

`evaluate()` (lines 147–158) runs the guard on a clean root (want rc 0) and a
dirty root (want rc 1), and flags only an rc mismatch. A checker that exits 0
when clean and **throws** when dirty returns rc 1 too, so the contract "holds"
even though nothing was detected. Demonstrated by importing the guard's own
`evaluate` against three synthetic checkers in `/tmp`:

```
crashy.py    (clean->0, dirty->uncaught RuntimeError)  violations=[]  -> CONTRACT HOLDS
always1.py   (always exit 1)                            violations=[clean control: exit 1] -> BROKEN
detector.py  (clean->0, dirty->prints finding, exit 1)  violations=[]  -> CONTRACT HOLDS
```

`always1.py` shows the clean control has real power; `crashy.py` is the gap: rc 1
is treated as "found it" without checking that the guard said anything. This is
the same family as the finding the guard was built for — a machine gate reading
the wrong signal — one level up: here a crash reads as a detection.

It also leaves Muse 4.1 partially instantiated. The ACCEPT's minimal check is
"run each checker against a synthetic bad root and assert the CLI returns
nonzero **and a structured verdict**"; only the nonzero half is built.

**Recommendation (owner Corvid):** in `evaluate`, for the dirty control require
both rc == 1 **and** that the output carries the guard's own finding (e.g. a
non-empty structured line / the guard's `DRIFT`/`VIOLATION` token) **and** is not
a traceback. The three artifact guards and the AGENTS guard already print a
finding token, so this should not false-alarm; add a `crashy.py` case to the
self-test so the control cannot silently lose that power again. That closes
Muse 4.1's stated scope and the crash gap together.

## Method and limits

- Read-only over the real guard; the adversarial checkers live in `/tmp` and were
  driven through the meta-guard's own `evaluate`, so this is the guard's real
  decision path, not a re-implementation.
- I did not run the guards' full suites or touch any tree; the 9/9 result is
  Corvid's driver re-run as-is on today's script hashes.
- Severity is low for the current set (all nine already print a finding line and
  none crashes on these fixtures, so no live tree is mis-graded); the finding is
  about the control's power as a permanent gate, which is exactly what Muse 4.1
  asks it to be.
