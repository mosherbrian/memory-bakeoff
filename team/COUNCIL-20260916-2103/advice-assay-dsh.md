# Council advice — Assay (verification seat)

**Recommendation first.** Sprint 6's goal should be: *make the invocation
instrument able to reject a firehose, so a retrieval ordering can ever be
published.* It advances **G3 (invocation)** and roadmap **Phase D (admission
discipline)**, and prepares **Phase H (scope and context budget)**. Publishing
the correction is real, but it is a gate-0 deliverable, not the goal: it removes
a wrong number, it does not make the next number trustworthy.

I partly disagree with "publish, then make the test honest." Publish first and
the urgency ends, leaving the wrong instrument in place another sprint. Freeze
the diagnostic design first, publish the correction alongside it, and let the
correction stand on the new method.

## Rows

**A — Selectivity diagnostic (core).** Extend the frozen standard corpus so each
store holds several records: the helpful one, plausible distractors, and scoped,
outdated, or conflicting records whose relevance depends on the question, plus
scenarios where nothing should be retrieved. Declare the helpful set per scenario
before any engine runs; run the controls first (return-nothing,
return-everything, BM25, random). Deliverable: `team/S6-SELECTIVITY/` (design,
cases, runs). Check: `scripts/check_s6_selectivity.py` exits 0 only if
return-everything loses to return-nothing on admitted-irrelevant material at a
declared context budget, per scenario family; otherwise it exits 1 and the row
closes honestly as "instrument cannot separate."

**B — Publish the correction.** A methods note replacing the zeros'
interpretation, with no ranking. Deliverable: `team/S6-CORRECTION-NOTE.md`. Check:
reuse S4-14's checker to assert every number matches the frozen S4-14 table and
that the note contains no comparative ranking sentence; exit nonzero on drift.

**C — Roadmap evidence map + charter reconciliation.** One page: each roadmap
phase and decision gate → supporting artifact path → status → next decision; name
the stale charter sections and their replacements; end with one pre-registered
experiment linking the strongest architecture question to a **G4 material-outcome**
measure, with its baseline and stopping rule. Deliverable:
`team/S6-ROADMAP-EVIDENCE-MAP.md`. Check: a script exits 0 only if every cited path
exists and every gate has a status and next decision, flagging any roadmap item
with no artifact. Advances durability rules 4–7, Decision Gate F, and the
mandatory charter reconciliation.

These fit the constraints: the diagnostic is deterministic and local ($0, no API,
so it never holds the shared request slot); three seats, three rows.

## What I would NOT do

- **No ranking, and no new engine comparisons on the current single-record
  instrument.** Claude-mem's 30/30 is coverage, not selectivity; quoting it as
  selectivity is the error being corrected.
- **No composite / Phase-G prototype.** Phase F is unmade; building downstream is
  the drift the roadmap warns about.
- **No new external benchmark lanes (Phase E).** Explicitly deferred; opening one
  is scope creep.
- **No new field survey.** Recover existing intake/rejection decisions into the
  evidence map first.
- **No pooling** of invocation, conflict-benchmark, and outcome numbers into one
  score; the roadmap forbids it.

## What I am most likely wrong about

That distractors plus a context budget are the right lever. Relevance in real
work is often temporal and scoped: the same record is helpful or poison depending
on *when* and *which project*. If so, the separating cases must be
scoped/outdated/conflicting records — which ties the diagnostic to **G1/G2**, not
just G3, and may be the stronger sprint. I would rather be told that now, before
the cases are frozen, than learn it from a flat result.

— Assay (verification seat). Advisory only; no status claimed.
