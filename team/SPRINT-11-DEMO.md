# Sprint-11 demo — the three questions narrow, and the native-state answer changes

Sprint goal (top of QUEUE.md): *Produce three pre-registered, independently
checked comparisons that narrow the abstention, external-benchmark and
native-state questions, without claiming they establish real-work benefit.*

This demo is judged against that goal, not against the count of work items.
The goal names three questions and one boundary. Each question is answered
below with its number, its caveat in the same breath, and what it means. The
boundary is stated plainly at the end. Finalized 2026-09-19 ~10:30 PDT.

**How the work was trusted.** Each comparison had an automatic check written by
a separate worker *before* the work existed, so a check cannot be fitted to a
finished result. Each result was then independently re-derived and confirmed by
a review worker who wrote none of it, against that pre-written check. That
machinery is the trust layer, not a result; the numbers below are the results.
All three comparisons were declared before any run, with the prior measurement
quoted beside the new one, so each is a re-measurement, not a guess with a
number attached.

## Question 1 — Abstention: does a non-token mechanism let BM25 decline? No, on this corpus.

Sprint 7 refuted the stopword filter. This sprint pre-registered a different
abstention *mechanism* — a declared score-margin rule (abstain when the top
score's margin over the corpus score distribution is under a threshold fixed
before any run) — and measured both sides the answer requires: irrelevant
queries rejected **and** useful retrievals lost, on the same frozen 10-case
corpus.

- At the declared threshold, the rule rejected **2 of 5** irrelevant queries but
  **lost 1 useful retrieval** — and the lost one scored *below* two of the
  abstain cases, so the margin does not order the families.
- The declared threshold grid, reported as data: **0.5 → 0 rejected / 0 lost,
  1.0 → 2 / 1, 1.5 → 5 / 2.** No declared threshold separates the families;
  rejections are always bundled with losses.

Caveat in the same breath: this is one frozen 10-case corpus, so it refutes the
mechanism *on this corpus*, not in general. But it is the same corpus the prior
cells were measured on, so the comparison is clean.

**What it means.** The read-the-scores family of abstention mechanisms is
refuted the way Sprint 7 refuted token filtering: the score distribution's
*shape* is not a discriminant here. The abstention question is narrowed from
"which mechanism" to "no declared score-reading rule separates the families on
this corpus," which points the next step away from reading scores.

## Question 2 — External benchmark: is the KnowledgeDrift weakness one system's? No.

The externally-authored weakness finding (retrieval 21/40, abstention 0/40,
rationale 5/40) was so far one system deep. This sprint replayed the same frozen
120-probe sample through the other pinned in-repo engines, family scores kept
separate, with the prior's BM25 cells reproduced as the control.

- The control reproduces the prior **item for item** (retrieval 21/40,
  rationale 5/40, abstention 0/40), so the harness did not move.
- The added engines, family-separate: **tf-idf 0.50 / 0.10 / 0.00, hybrid RRF
  0.50 / 0.07 / 0.00, dense LSA 0.275 / 0.075 / 0.00, claude-mem controlled core
  0.275 / 0.075 / 0.00** (retrieval / rationale / abstention).
- **Abstention sits at the floor, 0/40, on all five engines.**

Caveat in the same breath: this is one frozen 120-probe sample, and the
benchmark's author has a system in its own ranking, and it wins — the caveat
travels with the number.

**What it means.** The externally-authored weakness is no longer one system
deep; it is the flat ranked-retrieval shape itself. The finding generalizes
from "BM25 is weak" to "ranked retrieval, as implemented in these five engines,
does not decline" — the 0/40 abstention floor is a property of the retrieval
shape, not of one engine.

## Question 3 — Native state: does native pi-lcm falsely supersede on broader histories? Yes.

The state-layer answer's own limitation said broader histories were untested,
and the answer page requires native-failure evidence before any layer talk. This
sprint mechanically extended the prior trial generation (declared before the
run: more distractor families, longer streams, the documented distractor shape,
unfitted), ran the **native** pi-lcm arm only, no layer code, and reported old
beside new.

- On the declared broader corpus: **22/33 false supersessions (66.7%), 0/13
  missed updates.** Per family: mailbox-rename 11/11, roster-drift 11/11,
  ledger-amend 0/11.
- The prior, on its controlled corpus: **0/32 false supersessions, 0/12 missed
  updates.**

Caveat in the same breath: the broader corpus is declared and unfitted, and the
in-corpus control family (ledger-amend) measured **zero** false supersession —
a corpus fitted to fail would contradict itself, so the 66.7% is a real native
failure, not an artifact of the test.

**What it means.** The prior's 0/32 null does **not** generalize to broader
histories. There is now an observed native failure, and the state-layer answer
changes: the premise behind the prior "the layer fixes no observed problem" —
that no native failure was observed — is now false. The state-layer question is
re-opened, not closed.

## The boundary, stated plainly

None of these three is a real-work measurement. They concern abstention
quality, benchmark retrieval, and stored-state behavior. The goal asked for
comparisons that narrow the three questions *without claiming they establish
real-work benefit*, and that is exactly what they are. The question "does memory
improve real work?" remains **not established**; this sprint produced no new
evidence for or against it, and none of the numbers above should be read as
evidence either way.

## What is still open, plainly

- **The real-work question remains not established.** Its next discriminating
  step is the pre-registered matched outcome comparison against no memory, which
  is the one item here that is genuinely yours (see below).
- **The state-layer answer must absorb the S11-3 native failure.** The prior
  decision-ready to reject the state-layer rested on "no observed native
  supersession failure"; that premise is now false, so the reject is no longer
  decision-ready.
- **The abstention question is narrowed, not closed.** Two mechanism families
  are refuted (token filtering, score-reading); abstention still sits at 0/40
  across all five engines.
- **The external-benchmark weakness is now characterized** as the flat
  ranked-retrieval shape, but on one frozen 120-probe sample.

## Decisions, surfaced the way policy 5b requires

Not a list of asks. Each item below either carries a default the fleet will act
on if you say nothing (with its cap and its date), or is one of the two things
that are genuinely yours and may not be defaulted.

1. **The state-layer answer is re-opened by the fleet, not left on you.** This
   is a roadmap decision the fleet is entitled to make, so it is not an
   escalation. **Default:** the planner absorbs the S11-3 number into the
   state-layer answer at sprint close and withdraws the prior "reject the
   state-layer" decision-ready, because its premise (no observed native failure)
   is now false. **Cap:** $0 — a record update, inside the already-approved
   envelope. **Date it proceeds:** at sprint close, the next planner tick. You
   are notified, not gating.
2. **The real-work outcome step is genuinely yours, and is not defaulted.** It
   is the one item that uses your own work/sessions/data and a budget, so policy
   5b says it may not carry a default. Stated as a notification, not a proposal:
   the real-work question remains not established, and its next discriminating
   step (the matched outcome comparison against no memory) needs your
   private-data authorization and a budget/date before it can run. Nothing here
   proposes it as the next sprint; that is the planner's job.
