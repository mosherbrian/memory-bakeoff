# The first live paired Pi coding pilot

**Evidence class:** `architecture_pilot_paired_live`. Four invented tasks, two arms, three
repetitions, 24 runs, one local model. This is a mechanism pilot, not a coding benchmark and not
a model result. Nothing here generalises past these four tasks.

**The headline is negative, and the reason is not the one the design anticipated.** Arm B —
bounded composed context plus executable control — passed 7 of
12 verifiers against arm A's 12 of 12, and used *more*
cumulative context, not less. But the mechanism underneath is more interesting than the score,
and it splits cleanly in two.

## What ran

Qwen3.6-35B-A3B UD-Q4_K_XL (general.file_type 15, quantization_version 2), sha256
`707a55a8a4397ecd…`, on Vulkan0: AMD Radeon 8060S Graphics (RADV GFX1151), 127488 MiB total, server
version: 385 (2041049), sampling temp 0.6 / top_p
0.8 / top_k 20, reasoning
`off`, context 131,072. Pi 0.73.0 in an isolated agent
directory — the installed Pi carries the pi-lcm package, a tuned compaction configuration and thinking high; arm A is defined as stock Pi, so running against that configuration would have contaminated the baseline.

Every run: fresh worktree reset to the frozen tree, fresh Pi session, serial, 900s
timeout, network offline apart from the local endpoint.

## Seed policy: no seed, so these are samples

Sampling stays exactly as Gen44 pinned it: temperature 0.6, top_p 0.8, top_k 20, min_p 0. The three repetitions per cell are stochastic SAMPLES, not reproductions, and every comparison in this report is read that way.

Pi 0.73.0 exposes no seed anywhere in its provider or stream options, and the only injection point
would have put an extension in front of arm A's requests, which is exactly the baseline
contamination the rule forbids. **Every comparison below is between stochastic samples.** With
three per cell, a one-run difference is not a finding; a three-for-three pattern is worth naming.

## Compatibility smoke

Passed on the third attempt. The first two failures were mine, not the model's: the composed view
never showed the `state_revision` the patch protocol requires nor which fields were patchable, and
the rejection message named the fault without naming the remedy. Both were fixed before any frozen
task was exposed, and a cap was declared before the third attempt — one more repair, then publish
`compatibility_blocked`. No exposed `thinking`, `reasoning` or `reasoning_content` field appeared
in either arm's captured stream; that is a statement about exposed fields, not about hidden
internal reasoning.

## Result

| | arm A `pi_default_v1` | arm B `pi_state_control_v1` |
| --- | --- | --- |
| verifier passes | **12/12** | **7/12** |
| timeouts | 0 | 3 |
| request bytes, median | 52,638 | 64,757 |
| request bytes, mean | 65,450 | 321,832 |
| requests, median | 7.0 | 9.0 |
| tool calls, median | 8.0 | 11.0 |
| repeated or redundant calls, median | 0.5 | 1.0 |

By task, verifier passes and median cumulative request bytes:

| task | A passes | A bytes | B passes | B bytes | B timeouts |
| --- | --- | --- | --- | --- | --- |
| T1 | 3/3 | 26,291 | 3/3 | 65,804 | 0 |
| T2 | 3/3 | 52,938 | 0/3 | 26,591 | 0 |
| T3 | 3/3 | 126,929 | 1/3 | 1,164,745 | 3 |
| T4 | 3/3 | 43,215 | 3/3 | 63,711 | 0 |

Every pair, because averaging away the failures would hide the whole story:

| pair | A | B | bytes delta |
| --- | --- | --- | --- |
| T1 r1 | pass (20,445B) | pass (67,233B) | +46,788 |
| T1 r2 | pass (33,674B) | pass (50,003B) | +16,329 |
| T1 r3 | pass (26,291B) | pass (65,804B) | +39,513 |
| T2 r1 | pass (52,938B) | FAIL (23,407B) | -29,531 |
| T2 r2 | pass (53,910B) | FAIL (31,877B) | -22,033 |
| T2 r3 | pass (52,338B) | FAIL (26,591B) | -25,747 |
| T3 r1 | pass (126,929B) | FAIL (1,164,745B, timeout) | +1,037,816 |
| T3 r2 | pass (135,779B) | pass (1,055,608B, timeout) | +919,829 |
| T3 r3 | pass (115,035B) | FAIL (1,180,603B, timeout) | +1,065,568 |
| T4 r1 | pass (34,126B) | pass (63,711B) | +29,585 |
| T4 r2 | pass (90,731B) | pass (76,037B) | -14,694 |
| T4 r3 | pass (43,215B) | pass (56,366B) | +13,151 |

7 of 12 pairs agreed on outcome.

## The mechanism: per-request context is bounded, total work is not

This is the finding worth keeping.

| task | arm | requests | first request | last request | growth |
| --- | --- | --- | --- | --- | --- |
| T1 | default | 6 | 205 | 7,747 | 37.8x |
| T1 | state_control | 9 | 1,532 | 9,677 | 6.3x |
| T3 | default | 6 | 208 | 43,477 | 209.0x |
| T3 | state_control | 337 | 1,538 | 4,074 | 2.6x |

Arm A's request grows steeply with the run because the transcript is replayed — on T3, 208 bytes
to 43,477, a 209-fold increase over six requests. Arm B's does not: 1,538 to 4,074 over
**337 requests**. The bounded view works exactly as designed.

And that is why arm B loses. Its per-request context is flat, but it needs far more requests,
because each one starts from a composed view with a higher floor (about 1.5 KB against arm A's
200 bytes) and no memory of what the previous turns established beyond two interaction units and
the state the model bothered to write down. On T3 that becomes a loop: 337 requests, 591 tool
calls, 900 seconds, timeout, three times out of three.

So **H2 is supported and H1 is falsified at the same time**, and they are not in conflict: bounding
the size of each request did not bound the size of the run.

## The half of the treatment that never ran

Across all twelve arm B runs:

| control quantity | total |
| --- | --- |
| state patches accepted | 6 |
| state patches rejected | 3 |
| **transitions accepted** | **0** |
| transitions rejected | 0 |
| completions blocked by the artifact gate | 0 |
| artifact revalidations | 0 |
| Pi compactions cancelled | 0 |

Every one of the twelve runs ended in phase `inspect`. The model never requested a transition,
never recorded a receipt, and therefore never reached the completion gate. Six accepted patches
across twelve runs is the entire use it made of the control layer.

This has to change how the rest is read. Arm B as executed was **not** "state and control"; it was
a bounded context window plus three tools the model largely ignored. Its failures cannot be
attributed to control gating, because nothing was ever gated. H5 is untested rather than
supported: the artifact gate never fired because no completion was ever attempted through it.

Pi's own compaction never triggered either — these runs are far too short to reach it — so that
part of the treatment boundary was also inert.

## Hypotheses

- **H1 — B materially reduces cumulative request bytes.** Falsified here. B's median is
  64,757 against A's 52,638, and its mean is five
  times A's because of the T3 loops.
- **H2 — B reduces the growth of request size with run length.** Supported, strongly: 2.6x over
  337 requests against 209x over six.
- **H3 — B does not reduce success so far that the architecture is unusable.** Not met as
  configured. 7/12 against 12/12.
- **H4 — churn direction, exploratory.** B's median repeated-or-redundant calls is
  1.0 against 0.5; on T3 it is dominated by the loops.
- **H5 — the artifact gate prevents unearned completion.** Untested. No completion was attempted
  through the control layer.
- **H6 — a failure caused by missing older context is a first-class result.** Taken literally.
  T2 failed 0/3 while using *half* arm A's bytes and making zero repository mutations in the run
  inspected — it never made the coordinated edit. T3 looped. Neither the window nor the caps were
  touched afterwards.

## What this does and does not say

It says that this specific composition — two interaction units, a 4 KB state the model must
maintain by hand, and three tools it did not reach for — is not sufficient for this model on these
four tasks, and that bounding per-request context does not by itself bound the work.

It does not say the architecture is wrong. The control layer was never exercised, so it was never
tested. It does not say anything about a different model, a larger window, or a design where state
is written by the harness rather than volunteered by the model. Four tasks, three stochastic
samples each, one local 35B model at temperature 0.6.

Scientific digest `630dd36904a9bfbc329649c992316818bf902fd0f4bc33c27c38648c8d4ec6e5`, rebuilt with wall clock, cache warmth and host-local paths excluded.
