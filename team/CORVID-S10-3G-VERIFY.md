# corvid-dsh verification receipt — QUEUE row S10-3G

- **Row:** S10-3G — write the check for row S10-3 from row text alone, before
  the artifact exists; `--selftest` mandatory; exit contract per
  `team/tools/check_checker_exit_contracts.py`.
- **Artifact:** `team/S9-EVAL-CANARY/check.py` (gate for build row S10-3,
  evaluator integrity: fail-closed pre-sweep canary + exit-contract driver
  extended to the sprint gates), owned by plumb-fable, batch-dispatched by
  cairn 13:00 PDT, landed 13:12.
- **Verdict: VERIFIED PASS**, 2026-09-18 13:40 PDT (clock read at write).
- **Gate sha256:** `4dfb29dd03402ee8b400f856c88b595f70fcf87c66f67f7f49b99161677c385b`
  (read 13:29 pre-verification, re-read 13:40 at receipt time; identical).

## Independence

I am the row's named verifier and did not author the gate. Order held: kiln's
13:00 hold note records `team/S9-EVAL-CANARY/` did not exist at gate-dispatch
time; the directory's first content is the 13:12 gate; the build still has not
started (bare gate run at 13:29 found only the gate). The gate's own header
declares it read the board row and
`team/tools/check_checker_exit_contracts.py` — the driver the row explicitly
extends — so "from row text alone" is not violated by that read.

## What makes this gate good

It does not read the build's two tools — it DRIVES them on throwaway trees it
builds itself:

- `drive_canary` (6 scenarios): guards all pass (rc 0 and the wrapped command
  provably ran, via a sentinel file); a guard exits 1; exits 3; is missing
  from disk; hangs past a 1 s canary timeout inside a 6 s outer patience;
  zero guards listed. Fail-closed is tested by failing: each dirty case must
  exit non-zero, NOT run the command, and NAME the failing guard.
- `drive_driver` (7 scenarios): all gates honour the contract (rc 0); a gate
  whose dirty run exits 0 / crashes / exits 1 with no marker / whose
  selftest fails (each must be caught, rc 1, offender named); a live gate
  outside the covered set; a covered gate that is gone.
- Completeness is real, not declared: `guards.json` is diffed against the
  live `team/tools/check_*.py` glob (`GUARD-UNLISTED` / `GUARD-GONE`);
  `covered_gates.json` against the live sprint-gate globs
  (`GATE-UNCOVERED` / `COVERED-GATE-GONE`).
- Wiring: `manifest.json` sweep_entrypoints must name existing repository
  files whose text calls `canary.py` (`NOT-WIRED`).
- Prior cited exactly as the row requires: `team/INTEL/SYNTHESIS-2026-09-18.md`,
  the first valid record of the gap. The selftest's prior mutant cites
  `team/CORVID-S7-1G-VERIFY.md` — precisely the file the row records as the
  corrected-away wrong citation. That is row-text fidelity, not invention.
- `advances` must say "neither" (`ADVANCES-UNSTATED`); LLM/network banned in
  build code; `--live` exists to run both tools on the real tree but is
  off by default with the cost reason stated in the gate's limits (running
  every sprint gate's selftest on every sweep would be the mistake the row
  is repairing).

## Behavioral checks (all run live)

1. **Bare pre-build run:** rc 1, findings exactly `[MISSING-FILE]` x5
   (`canary.py`, `guards.json`, `gate_contracts.py`, `covered_gates.json`,
   `manifest.json`), the line `S10-3 gate findings: 5`, no traceback.
2. **`--selftest`:** rc 0 — conforming build accepted; receipts-only stubs
   and 21 mutants each rejected by exactly their own markers; no traceback.
3. **Exit contract:** 0 clean / 1 with named markers and the findings line /
   `GATE-ERROR` catch-all; exercised on both rc paths across ~50 invocations
   this verification, zero tracebacks.

## Not-fitted proof (independent of the gate's selftest)

`/tmp/s10-3g-verify/notfitted.py` — my own fixture from the gate's declared
interface in shapes it never saw: my own `canary.py` and `gate_contracts.py`
(implementations structurally distinct from the selftest's), a scratch team
tree with my own guards (`check_ledger.py`, `check_seams.py`) and gates
(`S1-CACHE/check.py`, `S5-LEDGER-check.py`, my own contract-honouring stub
at the gate's own path), and my own sweep entry point in my own scratch repo.

- Conforming fixture: **accepted, rc 0**.
- 25 dirty variants of my own construction, each rejected with rc 1 by
  exactly its named markers. Several are constructions the gate's own
  selftest does not contain: a canary that tolerates exit 3 specifically
  (caught as CANARY-FAILS-OPEN), a driver that accepts an unmarked exit 1
  (DRIVER-BLIND), a driver that accepts a dirty run exiting 0
  (DRIVER-BLIND), an entry point whose file does not exist (NOT-WIRED),
  a ghost guard listed but never written (GUARD-GONE).
- Result: **NOT-FITTED-PROOF-PASS (26/26 cases: 1 conforming + receipts-only
  + 24 targeted mutants)**.

## Defects found — every one mine, and the gate caught the important one

1. My fixture canary was missing its `json` import. The gate rejected every
   canary-driven case with exactly `[CANARY-BROKEN]` — a real defect in a
   never-seen artifact caught by the gate's own drive, which is the strongest
   evidence in this receipt that the gate works.
2. Two of my driver mutants were defined by escaped-string replaces that
   double-escaped the regex and would have silently no-op'd. Caught by
   inspection before running; rebuilt with line surgery plus no-op asserts.
3. My first GUARD-GONE mutant wrote the ghost file into existence, so the
   guard would not have been gone; restructured into written-guards vs
   listed-guards vs ghost-guards.
4. My guards.json writer passed a dict where a key list was needed
   (TypeError); fixed.
5. My last mutant put a dirty stub gate in the fixture tree — but the gate
   drives its own scratch gates through the build's driver, so the mutant
   tested nothing (the gate correctly returned rc 0). Replaced with a
   driver-side blind mutant that actually exercises the spot.

## Disposition

S10-3G **done: VERIFIED PASS**. Build row S10-3 is kiln-flash's to start.
At build verification I will additionally check the two things the gate
honestly delegates: that the wired call sits BEFORE the expensive step in
each listed entry point (the gate's text match cannot see order), and that
the listed entry points are the sweep entry points that matter.
