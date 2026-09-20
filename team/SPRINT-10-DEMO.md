# Sprint-10 demo — the door moves under realistic pressure, and the two reliability repairs are in

Sprint goal (top of QUEUE.md): *Establish whether stronger competing text changes
evidence delivery, make retrieval order visible, and repair the checks and
duplicate detection that keep research runs reliable.*

This demo is judged against those three clauses, not against the count of work
items. Each clause is answered below with its number, its caveat in the same
breath, and what it means. Finalized 2026-09-18 ~16:30 PDT.

**How the work was trusted.** Every piece of work had an automatic check written
by a separate worker *before* the work existed, so a check cannot be fitted to a
finished result. Each result was then independently re-derived and confirmed by
a review worker who wrote none of it. That machinery is the trust layer, not a
result; the numbers below are the results.

## Clause 1 — Does stronger competing text change evidence delivery? Yes.

Sprint 8's "pressure changed nothing" was narrow: that pressure never reached
the door. This sprint declared a harsher load that shares the queries' own
vocabulary (still containing no helpful evidence, declared before any run) and
re-measured the same five fixed items and three systems. Once the load competes
for relevance, evidence delivery collapses:

- **bm25** handed the model the helpful evidence in **5/5** cases normally, and
  **1/5** under the query-adjacent load.
- **pi-lcm tool-level** handed it in **1/5** normally (it delivers empty text on
  four of five — a measured property, not a bug) and **0/5** under the load: it
  now delivers nothing.
- **claude-mem** handed it in **5/5** normally and **3/5** under the load.

Caveat in the same breath: this is one declared load on one frozen five-item
corpus, not a general law. But it is the realistic shape of tool output in a
live agent session, so the Sprint-8 reading that "pressure is harmless" is
retired — the door's first clean result was "this pressure never reached the
door," not "pressure never matters."

**What it means.** The adopt decision on pi-lcm tool-level can no longer be made
from the retrieval score alone, and now carries a stronger caveat: under
realistic, query-adjacent competition it delivers the helpful evidence in 0/5
cases. That is the number the adopt call should be made against.

## Clause 2 — Is retrieval order visible? Yes, as a separate number.

Presence (was the evidence handed?) can stay flat while the evidence slides down
the ranked list. On claude-mem, presence held at **5/5** under the pressure load
while its rank measures moved — **MRR 0.80 → 0.90** and **nDCG 0.852 → 0.926**.
The evidence is there, but its position changed, and an order-blind report would
have printed only the flat 5/5 and missed it. These rank measures are now
separate numbers a report can carry, never blended into the existing scores.

Caveat in the same breath: this is the first report to carry them; no earlier
sprint report did, so there is no trend yet — only the current measurement.

**What it means.** A report can no longer hide a change in retrieval order behind
a flat presence number. Order is now visible and separate.

## Clause 3 — Are the checks and duplicate detection repaired? Yes, with two open ends.

**(a) The evaluator's protective checks now stop an experiment before it starts.**
The protective checks run fail-closed as a mandatory first step: if any guard
fails, the expensive experiment does not run. Working as designed, it immediately
surfaced **21 pre-existing failing guards** (unowned maintenance) that now block
the sweep until triaged. That is the repair doing its job — making unowned
maintenance loud — not a new defect.

**(b) The planner's duplicate detector no longer rejects genuinely new work.**
It had been mistaking an old rank citation for proof that new work was already
admitted, which stopped two planning attempts. It now keys on the candidate's
artifact path, so a fresh candidate over a previously used rank is accepted while
a true re-admission is still refused. Proven in both directions on a scratch
copy; the live board was never edited.

Caveat in the same breath: the fix is proven on a scratch copy but **not yet
deployed to the live planner** — the operator is mid-repair on the live tool, so
deployment is a one-line re-apply at their next checkpoint, not a straight
overwrite.

## What is still open, plainly

- The **21 pre-existing failing guards** block the pre-experiment sweep until
  each is triaged (repair, retire, or re-scope). This is unowned maintenance the
  repair made visible; it is not caused by this sprint's work.
- The **planner duplicate-detector fix** is proven but not deployed to the live
  planner.
- The **rank measures (MRR/nDCG)** are computed and reported here for the first
  time; they are not yet embedded in the standing sprint-close report path.

## Decisions waiting on you

The portfolio charter sat four days (written 09-12, approved 09-16) because
nothing raised it. I am surfacing the decisions that are waiting now so they do
not sit. Each is a decision for you, not for the fleet:

1. **The portfolio charter.** Approved 09-16 with a mandatory reconciliation
   follow-up. The reconciliation landed in the roadmap 09-17 (four sections
   marked superseded, three live). The charter file itself still reads DRAFT.
   Waiting on you: confirm the reconciliation satisfies the approval caveat so
   the charter is in force, and the campaign-2 window call that gates the
   charter's campaign (the outcome experiment).
2. **The adopt call on pi-lcm tool-level.** Now with the clause-1 number: under
   query-adjacent pressure it delivers the helpful evidence in 0/5 cases, while
   bm25 delivers 1/5 and claude-mem 3/5. Adopt as-is, does the delivery gap
   change the call, or hold until the post-2026-09-20 budget rule settles?
3. **The campaign-2 window call.** It gates the outcome experiment (does
   selectivity change real work) — the one unexecuted candidate that is ready
   except for your go.
4. **The SWE-chat download budget.** The last unexecuted candidate; it needs a
   download/storage decision (14 GB free against a 39.3 GB full-set projection).
5. **Close Sprint 8.** Its demo was filed this morning; the close confirm is
   still outstanding.

## One admin note

The artifact directories for this sprint carry `S9-` names (e.g.
`team/S9-DOOR-RUNG2/`) because the backlog's file paths were stale when the
sprint was admitted — the same defect class that caused Sprint 8's duplicate
close. The work is Sprint 10's; the directory names are cosmetic and do not
affect any number above.
