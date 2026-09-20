# S9-EVAL-CANARY design — evaluator integrity: the fail-closed pre-sweep
# canary, and the exit-contract driver extended to the sprint gates

Row S10-3 (admitted from BACKLOG-NEXT rank 9, 2026-09-18). Author: kiln-flash,
2026-09-18. Gate: S10-3G (plumb-fable, from the row text alone), VERIFIED PASS
by corvid-dsh 13:40 PDT (`team/CORVID-S10-3G-VERIFY.md`, gate sha
`4dfb29dd…`); cairn cleared the hold 15:03; claimed 15:10 PDT.

## Prior measurement (the row's own citation)

`team/INTEL/SYNTHESIS-2026-09-18.md` is the first valid record of both gaps:
nothing required the guards to pass BEFORE an expensive run, and the
exit-contract driver's covered set stopped at the sibling guards while the
S* gate checkers were exercised ad hoc by whichever seat verified (repeated
in `team/CORVID-S8-5G-VERIFY.md`, `team/CORVID-S8-6G-VERIFY.md`,
`team/CORVID-S8-7G-VERIFY.md`). An earlier draft named
CORVID-S7-1G-VERIFY.md for the second gap; that file carries no such
statement, and the record was corrected to SYNTHESIS-2026-09-18. Advances
neither a frozen goal nor a roadmap item directly — evaluator-integrity
repair underneath every measurement; said plainly per the row.

## The two tools and what fail-closed means here

`canary.py --team TEAM --manifest guards.json [--timeout S] [-- COMMAND …]`
runs every guard (each a `team/tools/check_*.py` under the same interpreter
with its argv; exit 0 is pass) and starts the wrapped COMMAND only when all
of them passed. A guard that exits non-zero, is missing from disk, or
exceeds the per-guard timeout is NAMED on stdout (`CANARY FAIL:
tools/check_<name>.py: …`), the command never runs, and the exit is
non-zero. A manifest listing zero guards is a failure in itself — checking
nothing is not a clean sweep. The command's exit code becomes the canary's.

`gate_contracts.py --team TEAM --covered covered_gates.json` drives every
covered sprint gate through the exit contract's two obligations:
`--selftest` exits 0 (the gate can fail AND pass), and a run on a target
that does not exist exits 1 while naming a `[MARKER]` and showing no
traceback. A live sprint gate outside the covered set, or a covered gate
gone from disk, is itself a failure — the sweep would have lost control of
it without noticing. Every failure names its gate; exit 0 only when all
hold. The globs are the gate's: `S*/check.py`, `S*-check.py`, `D-*/check.py`.

## The lists (generated from the live tree, 15:1x PDT)

- `guards.json`: all 27 `team/tools/check_*.py`, argv empty. The gate diffs
  this against the live glob; a guard added to tools/ must be appended here
  or the sweep says GUARD-UNLISTED.
- `covered_gates.json`: all 17 live sprint gates (D-7-timestamps,
  D-8-backlog, S6-CORRECTION, S6-ROADMAP, S6-SELECTIVITY, S7-BM25-PREFILTER,
  S7-COMPOSE, S7-KD-WORLDS, S7-STATELAYER, S8-DOOR, S8-HANDBOOK-PASS-check,
  S8-OPS-DEBT-check, S9-DOOR-RUNG2, S9-EVAL-CANARY, S9-RANK-DIAG,
  S9-SELECT-FIX, S9-STALEPATH-PROBES) — including this row's own gate,
  which is itself a live gate. A new S* gate must be appended here or the
  sweep says GATE-UNCOVERED.

## The wiring (before the expensive run)

This project had no persistent sweep runner — each row landed its own
harness — so the repair creates the wired path rather than pretending one
existed: `implementer/sweep.sh` (in the implementer lane, repository-relative
`implementer/sweep.sh`) invokes the canary FIRST and execs the expensive
command only on a clean guard set. Every expensive run in this lane goes
through it, or copies the same canary line ahead of its own entry script;
the next harness in the fleet (S10-4's proof.py) wires this call before its
first expensive step. The verifier's order check applies to the exec line:
the canary fully precedes the command it wraps.

## Cost model and limits, stated

The gate's default check drives both tools only on throwaway trees; `--live`
additionally runs them on the real tree — the canary then runs all 27
guards, and the driver runs 17 gates × (selftest + dirty run), which is the
cost the row is repairing, priced into the driver's 900 s per-gate timeout
rather than hidden. Limits: "calls canary.py" is a text match in the entry
point; whether the call sits before the expensive step (it does — the exec
follows the canary) and whether every expensive run is wired is the named
verifier's call. Guards and gates are checked as exit codes and text; the
canary does not interpret what a guard's failure means. No LLM, no network.
