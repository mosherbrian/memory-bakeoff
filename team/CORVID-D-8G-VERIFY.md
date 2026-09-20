# CORVID-D-8G-VERIFY — verification of row D-8G (the gate for D-8)

Verifier: corvid-dsh. Producer: plumb-fable, from row D-8G's text alone.
CONFLICT DISCLOSED UP FRONT: the artifact this gate judges (BACKLOG-NEXT.md)
is MINE. That is the point of the pairing — so this verification is built
around one question: can this gate FAIL? A gate that cannot fail would wave
my own file through by construction. It was proven able to fail, on my own
file, in six specific ways, before its clean verdict was accepted. And in
fact its FIRST live verdict was a correct FAIL of the then-current artifact —
the strongest independence evidence available, because the gate punished its
own author's artifact on first contact.

Real clock at write: 2026-09-17 12:3x PDT (read at the row edit).

## Verdict: VERIFIED PASS

## The gate's declared check

`python3 team/D-8-backlog/check.py --selftest` → rc 0: 21 fixtures — the
conforming board and the closed-sprint empty board ACCEPTED; prose-only,
piped check (plain and backtick-escaped), empty-while-open, prose check,
sentence-led check, command-not-on-box, TBD check, cannot-fail check, prose
artifact, no-goal-link, re-measure-without-prior, rank tie (in and across
tables), tie-mark rank, missing prior column, short row, binary junk, missing
file — each REJECTED by exactly its own marker, no traceback.

## Not-fitted check (the independence substance)

- No candidate-specific strings from any existing backlog anywhere in the
  gate; the contract in its docstring maps one-to-one onto row D-8G's text
  (declared artifact path + runnable check per candidate, goal/roadmap/
  neither, prior-or-none-exists, total order no ties, prose-only fails,
  piped-check cells fail, empty-list-while-open fails).
- Selftest fixtures are synthetic (B-1/B-2), not drawn from any real file.
- Default target resolved from `__file__`, not HOME or cwd — the same check
  from any seat (S4 rule honored; verified by running it from this sandboxed
  lane).
- Structural mtime independence (gate older than artifact) is impossible for
  this pairing by construction — the artifact landed 10:08, the gate 12:19:45
  — so independence rests on the not-fitted evidence above plus the
  first-contact FAIL below. Rests on evidence, not instruction, because the
  gate behaved contrary to its author's interest.

## The first-contact FAIL (recorded, not smoothed over)

The gate's first live run — before any verification — returned
`[PROSE-ONLY] no candidate table`, rc 1, against the backlog as it then
stood (prose-shaped: per-rank headings and bullets carrying the same
content). That verdict was CORRECT per the gate's contract, and it failed
work authored by the very seat the row text was written to protect the gate
from. The backlog was rebuilt to the contract (same ten candidates, same
ranks, same substance — change log disclosed in the file itself), not the
gate loosened. Second contact: `D-8 gate: clean (10 candidates, each
gateable, placed, and ranked without a tie)`, rc 0.

## Adversarial pass on the REAL artifact (my own mutants, not the selftest's)

Six degraded variants of the actual table, each rejected with rc 1, the
exact expected marker, the findings-count line, and no traceback:
prose check → CHECK-NOT-RUNNABLE; piped check → PIPED-CHECK; rank tie →
RANK-TIE; goal-less advances cell → NO-GOAL-LINK; n/a prior on a re-run
candidate → REMEASURE-NO-PRIOR; prose artifact → NO-ARTIFACT.
The clean verdict on the repaired file is therefore earned, not vacuous.

## Exit contract

rc 0 clean with the counted-candidates line; rc 1 with named `[MARKER]` +
`D-8 gate findings: N`; top-level catch converts any crash into
`[GATE-ERROR]` + rc 1 — a verdict, never a traceback, per
`team/tools/check_checker_exit_contracts.py`.

## Non-blocking observation

The gate is NOT yet registered in `team/tools/check_checker_exit_contracts.py`
(grep for D-8 finds nothing) — same follow-up class as the no-pipes guard
noted in my D-6 verify: the live team/tools suite should declare it so the
exit-contract suite covers it. Row text does not demand registration; filed
here so it does not get lost.

— corvid-dsh, 2026-09-17
