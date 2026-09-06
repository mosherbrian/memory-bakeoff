# Gen117: the first v5 reader run — NON_EVIDENCE, and why that is the good outcome

**Status: `NON_EVIDENCE`. No reader-effect result is claimed.**
Canonical artifact `results/gen117/attempt1`, manifest verifies, 7 artifacts.
Run time **95.9 seconds**, 60 calls, `qwen3.6-35b-vulkan-nothink`.

## What happened

Execution was clean. 60/60 `COMPLETED`, one served model, no transport failures,
no retries. Preflight passed every gate before the first call, and the execution
contract was frozen and hashed before exposure.

Then every one of the 12 cores failed its controls, so the run produced nothing:

| answer class | cells |
|---|---|
| `UNSUPPORTED_VALUE` | 42 |
| `CORRECT_INSUFFICIENT` | 12 |
| `CURRENT_WITH_HISTORY` | 4 |
| `CURRENT_ONLY` | 1 |
| `STALE_ONLY` | 1 |

## The cause is the fixture, not the reader

Canonical values are two words sharing a head noun — `sector marlow` /
`sector fenwick` — chosen so the pair would be lexically symmetric. The record
prose reads *"The Hyacinth corridor routes through sector fenwick."*

The reader answered `"selected_value": "fenwick"`.

Measured across the run: **36 of 48 selections dropped the head noun**, 6 matched
canonically, 6 were something else. The grader requires an exact canonical match,
so a correct answer expressed in its distinguishing token scored
`UNSUPPORTED_VALUE`.

The reader is very probably identifying the right record. It cited consistently
in 48 of 60 cells and abstained correctly in all 12 `INSUFFICIENT_CURRENT` cases —
which is the control that catches guessing, and it passed everywhere. What failed
is that the fixture asked a question whose correct answer has two acceptable
surface forms and the grader accepted only one.

## Why this is not repaired here

Sol's Generation 117 instruction: *"Do not repair a run-bearing semantic after
exposure."* Loosening value matching now, having seen the outputs, would be
tuning the ruler to the answers — the precise failure that produced the retracted
Gen114 headline. The 60 responses are sealed and the attempt is closed.

Any fix is a control-plane decision. The options, stated without preference:

1. **Single-token values.** Remove the shared head noun so the value has one
   surface form. Cleanest, but the head noun was there to keep the pair lexically
   symmetric, and removing it may reintroduce asymmetry.
2. **Accept the distinguishing token in the response contract**, declared before
   any run and applied to controls and treatment alike.
3. **Instruct the reader to echo the value verbatim** in the prompt, making the
   surface form part of the frozen protocol.

All three change a run-bearing semantic and so require a fresh freeze and a fresh
run. None may be chosen by looking at which produces a better score.

## What worked

The apparatus did the job it was built for. It failed closed, marked the attempt
`NON_EVIDENCE`, and refused to publish. Gen114, by contrast, ran to completion on
a defective ruler and produced a headline that stood for a day before retraction.

Cost of finding this: 96 seconds and one sealed attempt.
