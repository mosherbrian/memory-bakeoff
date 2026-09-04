# Harness-maintained state and control, live: the mechanism was the problem

**Evidence class:** `architecture_state_control_ablation_paired_live`. 24 live runs, four invented
tasks, two arms, three stochastic samples per cell, one pinned local model. A mechanism ablation,
not a coding benchmark.

**Arm C passed 12/12 with 0 timeouts. Arm B passed
9/12 with 3.** Same bounded composer, same caps, same tasks,
same model. The difference is who maintains the state.

## What changed between the arms

Both arms use the identical bounded composition Gen45 froze. B offers three tools and waits for the
model to drive state and control. C derives them from ordinary visible tool events and offers no
such tools. That whole bundle is the treatment; this report does not claim to isolate which part
of it did the work.

## Result

| | B `pi_state_control_v1` | C `pi_harness_state_control_v1` |
| --- | --- | --- |
| verifier passes | 9/12 | **12/12** |
| timeouts | 3 | **0** |
| reached control-valid `done` | 0/12 | **12/12** |
| provider payload bytes, median | 98,153 | 70,557 |
| provider payload bytes, mean | 921,295 | 126,156 |
| message/context bytes, median | 62,007 | 42,424 |
| requests, median | 8.5 | 6.5 |
| repeated or redundant calls, median | 1.0 | 0.0 |

By task, passes / timeouts / median payload bytes:

| task | B passes | B timeouts | B bytes | C passes | C timeouts | C bytes |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | 3/3 | 0 | 91,184 | 3/3 | 0 | 56,827 |
| T2 | 0/3 | 0 | 34,513 | 3/3 | 0 | 76,165 |
| T3 | 3/3 | 3 | 3,384,577 | 3/3 | 0 | 198,319 |
| T4 | 3/3 | 0 | 163,927 | 3/3 | 0 | 48,414 |

Every pair:

| pair | B | C | payload delta |
| --- | --- | --- | --- |
| T1 r1 | pass (91,184B, inspect) | pass (56,827B, done) | -34,357 |
| T1 r2 | pass (105,123B, inspect) | pass (59,191B, done) | -45,932 |
| T1 r3 | pass (69,159B, inspect) | pass (56,282B, done) | -12,877 |
| T2 r1 | FAIL (34,513B, inspect) | pass (85,015B, done) | +50,502 |
| T2 r2 | FAIL (34,559B, inspect) | pass (76,165B, done) | +41,606 |
| T2 r3 | FAIL (34,446B, inspect) | pass (64,950B, done) | +30,504 |
| T3 r1 | pass, timeout (3,384,577B, inspect) | pass (564,457B, done) | -2,820,120 |
| T3 r2 | pass, timeout (3,375,020B, inspect) | pass (198,319B, done) | -3,176,701 |
| T3 r3 | pass, timeout (3,509,713B, inspect) | pass (102,180B, done) | -3,407,533 |
| T4 r1 | pass (163,927B, inspect) | pass (48,414B, done) | -115,513 |
| T4 r2 | pass (164,725B, inspect) | pass (48,167B, done) | -116,558 |
| T4 r3 | pass (88,602B, inspect) | pass (153,910B, done) | +65,308 |

9/12 pairs agreed on outcome.

## H1: the mechanism actually ran this time

| arm B tool | runs that called it | total calls |
| --- | --- | --- |
| `propose_state_patch` | 3/12 | 3 |
| `record_receipt` | 6/12 | 6 |
| `request_transition` | 0/12 | 0 |

`request_transition` was called **zero times in twelve runs**, exactly as in Gen45, and no B run
reached a control-valid `done`. The model's non-adoption reproduced.

Arm C, on the same tasks, accepted **52 automatic transitions** with
0 rejected, created 14 receipts, invalidated
0, and ended with a receipt valid for the current tree in
12/12 runs. Every C run exercised the loop
(12/12 had at least one transition). H1 holds: event-driven
derivation does not depend on the model volunteering.

## H2: it also fixed what Gen45 blamed on the composer

Gen45 concluded that bounding each request did not bound the run, and that arm B looped on the
noisy task. The same composer, with harness-maintained state, does bound the run.

**T3** is the clearest case. B timed out 3/3 at a median 3,384,577
payload bytes — it did fix the repository, so the verifier passes, but it never stopped. C finished
every run at 198,319 bytes,
a 17-fold
reduction, and reached `done` from a valid receipt.

**T2** is the second. B failed 0/3 here in Gen45 and 0/3 again now. C passed 3/3. In Gen45 I
recorded that B's T2 failure looked like loss of persistent task intent; with the phase and the
recorded state maintained for it, the same composer and the same model completed the task.

So Gen45's negative result was about **who maintains the state**, not about the bounded view. That
is a real correction to the previous generation's leading suspect, and it only became visible
because C removed the dependency rather than repairing it.

## What this does not show

It does not isolate a subcomponent. C changes state maintenance, the instruction text and the tool
surface together. It does not say the architecture helps a different model, a larger task, or a
longer horizon: four invented tasks, three stochastic samples at temperature 0.6 with no seed, one
local 35B model. And C's advantage in bytes is partly an advantage in *turns* — it finishes sooner,
so it sends less.

Wall clock stays out of the reading: C adds a tree-digest call per tool result and the two arms
warm the prompt cache differently.

## Pre-exposure corrections

Two things were fixed before any task was exposed, both committed at `6a8fc13`.

**The tree digest was mutating the repository.** Arm C computed its digest with `git add -A`
against the real index on every tool result — observable to the agent through an ordinary
`git status`, and only in C. It now builds the same tree in a temporary index seeded from HEAD.
Proven equal to the old method across
clean, tracked_deleted, tracked_modified, untracked_added states, with `git status`
and the real index byte-identical across 100 calls, at
2.342 ms per call
(1.38 s across T3's 591-call scale,
against a 45 s gate). The old method visibly restaged:
`['M  pkg/core.py', 'A  pkg/new.py']`.

One caveat recorded rather than buried: the first non-mutation check reported a changed index hash.
That was the check's own `git status` refreshing the stat cache, not the digest. Isolated, the index
is byte-identical.

**Exit status was never bound.** Pi 0.73.0 surfaces no `exitCode` on this path at all, so the
derivation's primary branch is dead code and the live behaviour rides entirely on `isError`. A
known-failure and a known-success command both classify correctly, which was the stated condition
for accepting the fallback.

A provider-payload observer was added to both arms, which is why exact full payload bytes appear
above alongside the Gen45 message-byte measure. It returns nothing, and Pi's runner applies a
handler result only when it is not `undefined`, so it cannot rewrite a request.

Scientific digest `6063e3c857f213b1d6264318505b34882a10f9bd3489387ab2d3d5e3289cd9c8`, rebuilt with wall clock, cache warmth and host-local paths excluded.
