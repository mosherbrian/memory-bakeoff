# The human-direction floor, live: it did not earn its cost here

**Evidence class:** `architecture_human_direction_floor_ablation_paired_live`. 24 live runs, four
intent-persistence tasks, three stochastic samples per cell, one pinned local model. A mechanism
ablation, not a coding benchmark.

**Both arms passed 11/12 hidden verifiers.** Arm D, which carries the original
human instruction verbatim once the recent window drops it, cost more provider bytes and bought no
task-success improvement on this ruler. That is H3 as preregistered, and I am reporting it rather
than reaching for a ruler that would rescue it.

Two things did move, and neither is a success claim: D had **0 timeouts against C's
2**, and reached control-valid `done` **12/12 against
10/12**.

## Result

| | C `pi_harness_state_control_v1` | D `…_task_floor_v1` |
| --- | --- | --- |
| hidden verifier passes | 11/12 | 11/12 |
| timeouts | 2 | **0** |
| control-valid `done` | 10/12 | **12/12** |
| visible-receipt false assurance | 1 | 1 |
| failed requirement A / B | 0 / 1 | 1 / 0 |
| payload bytes, median | 78,682 | 84,911 |
| payload bytes, mean | 667,059 | 102,382 |
| requests, median | 6.5 | 7.5 |
| repeated or redundant calls, median | 0.0 | 1.0 |

By task — verifier passes, control-valid done, median payload bytes:

| task | C passes | C done | C bytes | D passes | D done | D bytes |
| --- | --- | --- | --- | --- | --- | --- |
| IP1 | 2/3 | 3/3 | 111,947 | 2/3 | 3/3 | 126,844 |
| IP2 | 3/3 | 2/3 | 72,044 | 3/3 | 3/3 | 72,743 |
| IP3 | 3/3 | 2/3 | 91,353 | 3/3 | 3/3 | 91,254 |
| IP4 | 3/3 | 3/3 | 57,533 | 3/3 | 3/3 | 57,973 |

Every pair:

| pair | C | D | payload delta |
| --- | --- | --- | --- |
| IP1 r1 | FAIL B | pass (floor) | +53,643 |
| IP1 r2 | pass | pass (floor) | +3,400 |
| IP1 r3 | pass | FAIL A (floor) | +4,237 |
| IP2 r1 | pass, timeout | pass (floor) | -4,790,803 |
| IP2 r2 | pass | pass (floor) | +699 |
| IP2 r3 | pass | pass (floor) | -9,681 |
| IP3 r1 | pass | pass (floor) | -99 |
| IP3 r2 | pass, timeout | pass (floor) | -2,252,425 |
| IP3 r3 | pass | pass (floor) | +214,004 |
| IP4 r1 | pass | pass (no floor) | +12,275 |
| IP4 r2 | pass | pass (no floor) | -11,558 |
| IP4 r3 | pass | pass (no floor) | +188 |

10/12 pairs agreed on outcome.

## Was the intervention even exposed?

The floor activated in **9 of 12** D runs, at a median request
5, costing 290 bytes per request
and 1,160 cumulative in the median exposed run. Three runs
finished before the window would have dropped the task, so their floor never activated; they are
`floor_not_exposed` and are **not** evidence either way. Exposed runs passed
8/9; unexposed passed
3/3.

That matters for reading the table: on a ruler where a third of runs end before the intervention
turns on, a null result is weaker evidence than 24 runs suggests.

## The one difference that is not noise

Each arm failed exactly once, and the failures were of different kinds. C's failure was
requirement **B** — the constraint that exists only in the human instruction. D's was requirement
**A**, the part visible in the code. One run each is an anecdote, not a finding, and I will not
dress it up as more; but it is the shape the ablation was built to detect, and it is the reason
this ruler is worth keeping rather than discarding.

## The completion gate finally disagreed with task truth

Both arms recorded **one `visible_receipt_false_assurance`**, and neither was on IP4, the task
built for it. Both were on IP1, where the shipped test encodes the old firmware ratio: the agent
updated that test, made it pass, earned a current-tree receipt and reached control-valid `done`
while still failing the hidden requirement.

That is exactly the frozen semantics doing their job. `control_valid_done` means a passing
recognised visible check for the current tree and nothing more. The artifact was valid evidence
for what it checked and incomplete evidence for the task — a limit of artifact authority, not a
control failure, and the hidden result never touched the control layer. It is worth noting the
diagnostic fired **naturally**, on a task not designed to produce it.

## Operations

C 2,194 seconds of run time, D 592, about
46 minutes of GPU-attached execution in total. C's
figure is dominated by its two timeouts; D's median run is
43 s against C's 41 s, which is not a meaningful
difference. Wall clock stays outside the scientific digest.

## What this does and does not say

It says that on this four-task ruler, with harness-maintained state already doing its job, keeping
the original instruction permanently resident did not improve hidden-verifier success and did cost
bytes. It does not say the floor is worthless: it removed two timeouts, took every run to a
control-valid completion, and the single failure it did suffer was not of the kind it exists to
prevent.

It says nothing about longer tasks, a different model, or a ruler where the instruction ages out
earlier and more often. The tempting next move is to build that ruler until the floor wins. That
would be shopping for a result, and this report declines to do it.

Scientific digest `4fd91e505b80f12a828a972d3cf4c8f995914b95a42762c483accb1c19176e5b`, rebuilt with wall clock and host-local paths excluded.
