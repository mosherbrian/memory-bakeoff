# DECISION ring: gen120-review-severity

- taken: 2026-09-06T15:29:45-07:00
- commit: 923365c255152bb527290e0ed4acfec79ab71562
- kind: ring

# Honour the reviewers' own severity, rather than treating every finding as blocking

## What I chose

`DEFECTS_BLOCKING` from either reviewer still blocks the handoff. `DEFECTS_MINOR`
no longer does: each finding is recorded in the ledger with status `CARRIED`,
which is visible, owned, and carried into the next generation. The doorbell
accepts `PROCEED` or `CARRY`, refuses `FIX FIRST`, and still refuses on any row
marked `OPEN`.

## What I rejected

Leaving the rule as written (every DEFECTS_MINOR blocks until a clean round).

## The evidence

Five blind review rounds on Gen120. **Not one returned DEFECTS_BLOCKING.** Every
round, both reviewers independently wrote that the published result stands. My
rule treated that as a blocker anyway, which collapses the exact distinction the
three verdict tokens exist to draw - I was overriding the reviewers' severity
judgement and then citing their verdict as the reason to keep going.

Counted across the 32 Gen120 findings: about 8 could have corrupted real data
(raw evidence outside the verifier, the marker asserting rather than measuring,
the balance gate tolerating then under-enforcing, and the malformed-200 retry
that would have resampled a live run until it parsed). All 8 are fixed, and both
reviewers confirmed each fix independently. The remaining ~24 are stale docs and
overclaims (10), naming and labels (6), test quality (5), and process (3).

About 10 of the 32 were defects I introduced, and every one of those came from
machinery I ADDED rather than from repairs to existing code - including two in
the guardrails I wrote mid-review. The loop does not converge while the reviewer
surface keeps growing, because I keep growing it.

The cost of the old rule is the thing that matters: the experiment has not run
since Gen117. Thirteen freezes, a control plane, an escalation ladder and ~1,475
tests have produced zero new scientific data about the actual question.

## Why this is not a self-serving weakening

It is exactly the kind of change the rivals exist to catch, so I did not make it
on my own authority. I put the reasoning to Brian, including the counts above and
my own error rate, and he authorised proceeding on 2026-09-06. The gate keeps
full force for `DEFECTS_BLOCKING`, nothing is dropped silently, and the reader run
remains gated on the control plane regardless of what this rule says.
