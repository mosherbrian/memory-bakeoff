# corvid-dsh verification receipt — QUEUE row S10-4G

- **Row:** S10-4G — write the check for row S10-4 from row text alone, before
  the artifact exists; `--selftest` mandatory; exit contract per
  `team/tools/check_checker_exit_contracts.py`.
- **Artifact:** `team/S9-SELECT-FIX/check.py` (gate for build row S10-4,
  planner integrity: sprint-next's duplicate detector keyed on candidate
  identity, not rank number), owned by plumb-fable, batch-dispatched by cairn
  13:00 PDT, landed 13:18.
- **Verdict: VERIFIED PASS**, 2026-09-18 13:50 PDT (clock read at write).
- **Gate sha256:** `eb049906eba0644c67bebced314091a3de09e7c813178112245196339b136540`
  (read 13:41 pre-verification, re-read 13:50 at receipt time; identical).
- Verified without a verdict-wanted wake: the poller's 13:41 wake led with
  the three already-stamped gate rows; this gate had landed at 13:18 and the
  12:54 standby note commits this seat to verify each check the moment it
  lands, so it was verified on that evidence rather than on a wake.

## Independence

I am the row's named verifier and did not author the gate. Order held: kiln's
13:01 hold note records `team/S9-SELECT-FIX/` did not exist at gate-dispatch
time; the directory's first content is the 13:18 gate; the build still has
not started (bare gate run at 13:41 found only the gate). The gate's header
declares it read the board row and the tool it repairs
(`~/.config/agent-deck/sprint-next`'s `already_admitted` and SN_* settings) —
the row itself names the tool and the function, so that read is within "from
row text alone".

## What makes this gate good

It is an instrument, not a reader. It loads each tool copy in a subprocess
with `SN_TEAM` / `SN_QUEUE` / `SN_DIR` pointed at a gate-written scratch
board, and calls the real function, `already_admitted`, on four candidates:

1. the same artifact re-declared under a NEW rank — must be refused
   (`READMISSION-ADMITTED` when not);
2. the same artifact under the same rank — refused likewise;
3. a fresh artifact over a burned rank number — must be ADMITTED
   (`FRESH-REFUSED` when not);
4. a fresh artifact at rank 1 while the board cites rank 12 — admitted.

Case 4 is the exact shape of the fleet's real 11:04 and 12:27 false
refusals. Then:

- **The bug was there:** the pre-fix copy is driven the same way and must
  refuse case 3 (`BEFORE-NOT-BUGGY`), and the two copies must differ in
  `already_admitted` (`NO-FIX`) and NOWHERE else — an AST comparison over
  everything outside that function (`FIX-NOT-SCOPED`), the fleet-script
  discipline.
- **The proof can fail:** the build's `proof.py` must exit 0 on the patched
  tool (`PROOF-FAILS`) and non-zero on the pre-fix copy
  (`PROOF-CANNOT-FAIL`), and must show scratch mechanics — an SN_* override
  or a temp directory (`PROOF-NOT-SCRATCH`).
- **Live-board safety is measured, not promised:** the gate counts the
  board's own sprint-next traces (admission lines and `.bak-sprintnext-*`
  backups) before and after running the proof (`LIVE-BOARD-TOUCHED`).
- **Deployment honesty:** `deployed: true` requires `deployed_paths`, and
  every deployed path is DRIVEN through both directions
  (`LIVE-TOOL-UNFIXED`); `deployed: false` requires a handoff naming who
  deploys and where (`NOT-DEPLOYED-NO-HANDOFF`).
- **Prior and scope:** `manifest.json` prior must name BOTH dead proposals
  (`PRIOR-NOT-CITED`); advances must say neither (`ADVANCES-UNSTATED`).

Two honest boundaries, stated in the gate itself: a re-pointed candidate
(same rank, other path) is REPORTED in the clean-run summary, not judged —
the row defines that rule and the rank test was added 2026-09-17 for exactly
that case; and live-board safety is judged by sprint-next's own trace kinds,
so an edit of another kind would not be seen. Both printed on a clean run.

## Behavioral checks (all run live)

1. **Bare pre-build run:** rc 1, findings exactly `[MISSING-FILE]` x4
   (`sprint-next.before`, `sprint-next`, `proof.py`, `manifest.json`), the
   line `S10-4 gate findings: 4`, no traceback.
2. **`--selftest`:** rc 0 — TWO conforming builds accepted (deployed, and
   not-deployed-with-handoff); a receipts-only directory and 16 mutants each
   rejected by exactly their own markers; no traceback. Every mutant
   corresponds to a way the row can be genuinely failed: fix never made,
   over-fix that refuses nothing, unscoped patch, pre-fix copy already
   fixed, proof that always passes / never uses a scratch board / writes to
   the live board, undrivable tool, stale or absent deployment, handoff
   omitted, priors, JSON/schema/missing-file.
3. **Exit contract:** 0 clean / 1 with named markers and the findings line /
   `GATE-ERROR` catch-all; exercised on both rc paths across ~60
   invocations this verification, zero tracebacks.

## Not-fitted proof (independent of the gate's selftest)

`/tmp/s10-4g-verify/notfitted.py` — my own stand-in planner pair (buggy and
fixed `already_admitted`, my own code shape, differing only inside that
function), my own `proof.py`, my own manifest and scratch board, written
from the gate's declared interface. Both conforming variants (deployed, and
handed off) accepted rc 0; 17 dirty variants of my own construction each
rejected with rc 1 by exactly their named markers, including shapes the
gate's selftest does not build (a proof that asserts the wrong direction
outright; a tool that tolerates exit 3 is S10-3G's domain — here: an
over-fix with an early `return None`, an unmarked-exit proof variant).

- Result: **NOT-FITTED-PROOF-PASS (20/20 cases: 2 conforming + receipts-only
  + 17 mutants)**.

## Defects found — every one mine; the gate caught the two that mattered

1. **My "fixed" tool was still buggy.** My repaired rank test checked the
   rank per row but omitted `art in line` from the same condition — so a
   fresh candidate was still refused whenever ANY row cited the burned rank.
   The gate rejected my CONFORMING fixture with exactly
   `[FRESH-REFUSED, PROOF-FAILS]`. That is the not-fitted test working at
   full strength: a check fitted to a finished artifact would have passed
   my broken fix, because a broken fix is what a hurried author writes.
2. **My vandal proof could not vandalize.** I derived it from the
   un-substituted template, leaving a literal placeholder that crashed the
   proof before it wrote anything — the gate returned `[PROOF-FAILS]`
   instead of the expected `LIVE-BOARD-TOUCHED`, and on inspection the
   crash was real. Re-derived from the clean proof; then caught, as
   designed.
3. Harness plumbing, mine only: a stray quote (SyntaxError), a guards
   writer that passed a dict where keys were needed, a placeholder left
   un-indented (IndentationError in the over-fix stand-in), an inverted
   main guard, and a lost `MUT = [` line from a partial edit. All fixed;
   none touch the gate.

## Disposition

S10-4G **done: VERIFIED PASS**. Build row S10-4 is kiln-flash's to start.
At build verification I will additionally check the two things the gate
honestly delegates: that the deployed/handoff choice matches what the
operator actually wants done with the patched tool (the row says the tool is
under active repair by its operator today), and that no trace kind outside
sprint-next's own was left on the live board.
