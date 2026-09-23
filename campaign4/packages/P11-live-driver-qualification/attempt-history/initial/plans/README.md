# P11 plans: the P10 plans with F1, F2 and F3 corrected

Source 1341f04 and binary c1c49a29 are unchanged. The historical P10 files are unchanged.
`evidence/live-driver.diff` is the full driver diff. `evidence/rename.diff` holds the other files;
they differ from P10 only by the rename P10 -> P11 (`evidence/rename-only-check.txt`).

| Finding | Correction in `live-driver.sh` | Executable evidence |
|---|---|---|
| F1 captured stdout | `out()` logs to driver.log only. `verdict()` prints `PARSE-ERROR` and returns 1 for missing, empty, malformed or verdict-less state. A timed-out `wait_for` writes a `wait:<label> INCOMPLETE` row. The run exits 1 if any row is FAIL or INCOMPLETE. A DRY run writes only DRY rows. | `evidence/f1-helpers.sh` runs the real helpers, not in DRY mode: P10 10 PASS / 19 FAIL, P11 29 PASS / 0 FAIL (`f1-helpers.txt`) |
| F2 wall-stop | The driver re-execs itself in the owned scope `p11live-driver-$RUN.scope`, and checks that `/proc/$$/cgroup` names it. The wall timer is armed with `AccuracySec=1s` and the driver's PATH, and it is checked active before any effect; otherwise SETUP FAIL. The wall stops the scope (the driver and all children), writes `WALLSTOP INCOMPLETE`, then cleans up. Cleanup takes a lock, so it runs once. A TERM from the wall skips the driver's own cleanup. | `evidence/f2-wallstop-witness.sh`: P10 wrote 10 effects after the bound, including an L1 dispatch, and its driver stayed alive (`f2-wallstop-p10.txt`). P11 wrote 0 late effects, 1 WALLSTOP row and 1 cleanup, left the driver and its children dead, and a second cleanup did nothing (`f2-wallstop-p11.txt`). With arming refused: SETUP FAIL and no effects (`f2-arm-failure.txt`) |
| F3 L2 open work | L2 runs for 3 min. After the kill checks, which are unchanged, L2 settles through its own deadline timer to `timed-out`. That step is not open work. The `L2-settle` row checks one /cancel and one director wake. Rest is then required. There is no decide: the core refuses it in both RUNNING and BLOCKED phases. | `evidence/f3-go-settlement.sh`, run on the frozen CLI with injected transport: 15/15 (`f3-go-settlement.txt`) |

`evidence/construction-dry/` shows command construction only (DRY): 14 DRY rows. It is not behavioural evidence.
