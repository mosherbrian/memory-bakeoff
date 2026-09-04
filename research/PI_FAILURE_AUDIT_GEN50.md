# What actually went wrong: an audit of six live runs

**Evidence class:** `architecture_failure_mechanism_audit_posthoc_no_score`. No model, no GPU, no
network, no new runs. This reads evidence already paid for in Gen47 and Gen49.

Three generations moved a context knob and measured the outcome. None had read what the agent
actually did. **Across five failures, not one was caused by missing context.**

## First, an integrity failure of my own

The Gen47 and Gen49 raw provider streams are gone. The script that computed their hashes deleted
the files it had just hashed, and for Gen49 it ran against the workstation copy, so no copy
survives. Both manifests said the streams were "retained on the Linux workstation". That sentence
was false when it was written, and my own code made it false.

The manifests now carry a correction and `streams_still_exist: false`. Gen45's streams do survive,
because that manifest was computed against the Mac copy alone — which is the accident that reveals
the bug.

This audit therefore could not read a single model utterance. It was done entirely on the committed
harness logs: tool calls with their arguments, provider request sizes, derivation events, receipts,
tree digests and verifier outcomes. That turned out to be enough for all six cases — but that is
luck, not design.

## The six cases, frozen before anything was read

| case | verifier / status | tool calls | mutations | visible checks | primary mechanism |
| --- | --- | --- | --- | --- | --- |
| `gen47-T2-r1-B` | False / completed | 8 | 0 | 0 | `tool_sequence_or_verification_gap` |
| `gen47-T3-r1-B` | True / timeout | 584 | 1 | 259 | `termination_detection_loop` |
| `gen49-IP1-r1-C` | False / completed | 10 | 2 | 1 | `present_but_not_used` |
| `gen49-IP1-r1-D` | True / completed | 17 | 3 | 2 | `not_a_failure` |
| `gen49-IP1-r3-D` | False / completed | 14 | 4 | 2 | `coding_or_reasoning_error_with_sufficient_evidence` |
| `gen49-IP2-r1-C` | True / timeout | 442 | 1 | 1 | `termination_detection_loop` |

## What the failures actually were

| mechanism | cases | which |
| --- | --- | --- |
| `coding_or_reasoning_error_with_sufficient_evidence` | 1 | gen49-IP1-r3-D |
| `present_but_not_used` | 1 | gen49-IP1-r1-C |
| `termination_detection_loop` | 2 | gen47-T3-r1-B, gen49-IP2-r1-C |
| `tool_sequence_or_verification_gap` | 1 | gen47-T2-r1-B |

**Zero** cases were `missing_relevant_context`. In every failure the relevant public information was
either in the live provider payload or in a file the agent had already read.

### Two runs finished the work and could not stop

`gen47-T3-r1-B` made its single mutation — the correct fix — at tool call **314 of 584**, then made
**269 more calls, 261 of them bash, with zero mutations**, until the timeout.

`gen49-IP2-r1-C` is starker. Its only mutation was at call **6 of 442**, and it contained both
required changes. It then made **435 more calls, 434 of them bash, with zero mutations**, while
**holding a receipt valid for the current tree** and sitting in phase `validate`.

The repository was correct and untouched for 46% and 98% of those runs respectively. Neither is a
context failure in any form. In the second case the harness had already computed the stop
condition and recorded it; nothing consumed it.

### One run never started

`gen47-T2-r1-B` made four requests, eight tool calls and **zero mutations**, ending in phase
`inspect`. The instruction was present and the code was readable. It simply stopped before
attempting the work — and nothing in the run treated "has mutated nothing" as abnormal.

### Two runs had everything they needed and got it wrong

`gen49-IP1-r1-C` is the case Gen49 was built to test, and it answers Gen49's question directly. The
agent read `telemetry.py` at tool call 4, then at the critical point changed the single constant
`STEPS_PER_MM = 4 → 8` that both consumers share — breaking the telemetry requirement. It then
edited the visible test to match and ran **only that one test file**, earning a valid receipt and
control-valid `done`. The instruction had **not** aged out; it was six requests into the run and
still in the window. **A human-direction floor could not have helped**, which is precisely why
Gen49 found nothing.

`gen49-IP1-r3-D` had the floor active and carrying the instruction verbatim, and still inverted
which constant belonged to which consumer across four mutations, one of them a revert. Presence is
not use.

### The successful comparator differs by verification breadth, not by context

`gen49-IP1-r1-D`, the paired success, did two things differently: it gave telemetry its own
constant, and it ran the **whole tests directory** rather than one file. The floor was also active,
so a single pair cannot separate those. But the breadth of the check tracks the outcome here, and
the instruction's presence does not.

## Does any of this argue for retrieval?

No. none. In all five failures the relevant public information was in the live context or in a file the agent had already read; no case required anything that had aged out of the window

On the evidence in front of me, on-demand history retrieval should stay deferred. Nothing in these
six runs would have been rescued by reaching further back.

## The one invariant this audit does suggest

`quiescent_completion`: when a valid visible receipt exists for the current tree digest and K consecutive provider requests produce no repository mutation, the run has nothing left to do

It would have affected `gen47-T3-r1-B`, `gen49-IP2-r1-C`,
and both quantities it needs — receipt validity against the current tree digest, and mutation count
since — are **already computed and recorded** by `harness-state-v1`. It needs no hidden verifier and
no new context.

The caveat matters as much as the proposal: this would end runs sooner, not make them more correct; on IP1-r1-C it would have stopped a run that was already wrong It would
make runs shorter, not more correct. It is not implemented here.

## The honest summary

The context-memory thesis gets no support from this audit. Two failures were termination, one was
never starting, and two were the agent having the right information and using it wrongly — one of
them with the instruction sitting verbatim in its context. The remaining architectural gap these
runs actually expose is about **knowing when to stop and how broadly to verify**, not about what
the model can see.

Audit digest `6863d0291d865647bc81dab857cae76fcaaabdbecf0d29c168e809f5c7531744`.
