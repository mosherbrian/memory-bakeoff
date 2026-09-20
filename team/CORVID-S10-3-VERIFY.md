# CORVID-S10-3-VERIFY — build verification of row S10-3

corvid-dsh, 2026-09-18 15:4x PDT. Verdict: **VERIFIED PASS** (two stated tree
events, §5–6, neither a defect in this build). Row S10-3 ("Evaluator integrity:
wire the guard set as a fail-closed pre-sweep canary step and extend the
exit-contract driver to the sprint gates"), owner kiln-flash, artifact
`team/S9-EVAL-CANARY/` plus the wired entry point `implementer/sweep.sh`. Gate
S10-3G was verified by this seat 13:40 PDT (`team/CORVID-S10-3G-VERIFY.md`);
the gate is unchanged.

## 1. Gate

- `check.py` sha256 `4dfb29dd03402ee8b400f856c88b595f70fcf87c66f67f7f49b99161677c385b`
  — identical to my 13:40 gate verification and to the value kiln quoted at its
  15:18 close.
- Declared check re-run by me 15:34 PDT: rc 0 CLEAN ("27 guards listed, 17
  gates covered, 1 sweep entry point(s) wired; canary driven on 6 trees, driver
  on 7").
- Mandatory `--selftest`: rc 0, PASS — conforming build accepted; receipts-only
  directory and 21 mutants each rejected by exactly their own markers; no
  traceback.

## 2. canary.py — fail-closed rehearsed with my own fixtures

All four contract paths exercised with fixtures under a fresh temp `team/`
(Python guards — the canary runs each guard under `sys.executable`, so a
shell-script guard fails as an OSError-class nonzero; my first fixture attempt
tripped on exactly that, which is contract-consistent behavior, recorded here
as an owned lesson):

| rehearsal | result |
|---|---|
| one guard exits 3 | `CANARY FAIL: … exit 3 :: boom: deliberate failure`, rc 1, sentinel file NOT created — command did not run |
| hung guard, `--timeout 1` | `CANARY FAIL: … exceeded the 1s canary timeout`, rc 1, command did not run |
| missing guard file | `CANARY FAIL: … guard missing from disk`, rc 1 |
| all guards pass, command `sh -c 'exit 7'` | command ran; canary rc 7 — exit propagation holds |
| empty guards manifest | `guards manifest lists no guards: nothing was checked`, rc 1 — checking nothing is a failure |

Code read confirms fail-closed by construction: the command is only reachable
past the `if failures:` block; every failure is named with its guard path.

## 3. gate_contracts.py — driver rehearsed with my own fixtures

| rehearsal | result |
|---|---|
| conforming mini-gate covered | rc 0, "1 of 1 hold" |
| covered gate gone from disk | `CONTRACT FAIL: … covered gate is gone from disk`, rc 1 |
| live sprint gate outside covered set | `CONTRACT FAIL: … live sprint gate outside the covered set (no control over it)`, rc 1 |
| gate whose dirty run exits 0 (fails open) | `CONTRACT FAIL: … the contract (exit 1, a named [MARKER], no traceback) is not honoured`, rc 1 |

Cosmetic, not a defect: when the live-outside-set and covered-gone classes fire
together the held count prints negative ("-1 of 1 hold"); the exit code and the
named failures are correct either way.

## 4. The row's named crux — exec-line ordering and the wired entry point

`implementer/sweep.sh` execs `team/S9-EVAL-CANARY/canary.py --team team
--manifest team/S9-EVAL-CANARY/guards.json --timeout 120 -- "$@"`. The wrapped
command is an argument TO the canary, so no path reaches the expensive step
without the canary having passed: the ordering property holds structurally, not
by convention. The manifest's wiring note is honest that this project had no
persistent sweep runner and the repair creates the wired path. One observation:
sweep.sh is mode 644 (not executable); its documented usage is
`sh implementer/sweep.sh -- …`, so nothing is breached.

## 5. Live-tree reproduction (independent of kiln's runs)

- Driver on the live tree: `gate contracts: 17 of 17 hold`, rc 0 (104s wall) —
  matches kiln's reported GREEN.
- Canary on the live tree with the real guards.json: rc 1, exactly **21**
  `CANARY FAIL` lines, "the wrapped command did not run" — matches kiln's
  reported 21-of-27 fail-closed. I did not re-triage the 21 (pre-existing
  guard/tree drift; per-guard repair/retire/re-scope is cairn/Brian triage per
  the row).

## 6. Tree events during verification (neither is a build defect)

- **Mid-verification drift, named by the design.** `team/tools/check_answer_provenance.py`
  was created at 15:38 PDT — after guards.json was generated (15:13:54), after
  kiln's close (15:18), and after my first clean gate run (15:34). It is a real
  new guard (an ANSWER.md provenance checker citing Brian's 2026-09-18
  progression concern) not yet registered in QUEUE.md/BOARD.md. Re-running the
  declared check at 15:41 now returns rc 1 `[GUARD-UNLISTED]` naming exactly
  that file. This is the repair working on its own artifact: the gate names the
  gap, and sweep.sh blocks an expensive run until the manifest is regenerated.
  The manifest is stale by exactly one guard as of 15:41; regenerating it
  changes the artifact after close, so I did not do it — the named gap is the
  designed state until cairn/Brian triage or a manifest-regen row.
- **Pre-existing live-tree guard failures (the 21)** were present before this
  row and are unchanged by it; kiln's four drift classes were consistent with
  my sample reading of the failure lines.

## 7. Verdict

VERIFIED PASS. The build does what the row says: guards run fail-closed before
any wrapped command, the driver now controls all 17 live sprint gates, and the
wired entry point enforces the ordering structurally. Limits: my rehearsal
fixtures are synthetic (small, hermetic); the live-tree claims are reproduced
once each; and §6's drift means the gate is red again as of 15:41 by design
until the guard manifest catches up with the new `check_answer_provenance.py`.
