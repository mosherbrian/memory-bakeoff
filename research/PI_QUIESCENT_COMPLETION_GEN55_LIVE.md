# Gen55 — the corrected stop rule, live

Evidence class: `architecture_quiescent_completion_tracked_digest_paired_live`.
Base commit `fd227b5`. 24 live runs on the local Strix Halo under standing authorization.

## The story so far, in plain words

An automated coding agent that cannot tell when it has finished will keep going. We audited five
failed runs and found that none of them failed for lack of information — two had done the job and
simply could not stop, one making its correct fix at tool call 314 of 584 and then making 269 more
that changed nothing.

So we wrote a rule using only things anyone can see: *the project's own tests passed, nothing has
changed since, and three more actions have gone by without changing anything — stop.*

Letting that rule stop runs for real, three generations ago, found two defects that no amount of
offline calibration had shown.

**It stopped a run that had undone its own work.** The agent made the correct fix; the project's own
out-of-date test rejected it, so the agent put the old value back, the stale test went green, and
the rule ended the run on a codebase identical to the one it started with. The rule had asked only
whether *an edit happened*, never whether *anything had changed*.

**It could not see the stall it was built for.** Another run ran the same passing test 144 times and
timed out. Every pass looked like fresh news and reset the patience counter, so the loop never
accumulated three quiet actions.

We repaired both, and the second repair worked immediately. The first did not, for a reason that
took another generation to find: the way we fingerprinted "the codebase" counted files that *running
the tests creates*. Python leaves compiled bytecode behind. So running the tests moved the
fingerprint on its own, and the run that had reverted itself still looked changed. Correcting the
fingerprint to ignore build output — while still noticing a genuinely new file — made the refusal
real: replayed over all 72 recorded runs, the reverted run became ineligible at every patience
setting, the 144-repeat stall was still caught, and nothing was stopped while still making progress.

That was the agreed condition for trying it live. This generation does that.

## What is being compared

Two arms, one difference. Arm C is the harness-maintained state and control baseline, unchanged
since Gen47 and still hashing to the Gen48 freeze `205279d9…`. Arm F is arm C plus the completed
stop controller and nothing else:

- `quiescent-completion-toolcall-v2` semantics;
- K = 3, counted in tool calls;
- `tracked-tree-digest-v1` as the fingerprint;
- the quiescence snapshot written on every tool result, atomically;
- the safe stop that waits for an in-flight batch to drain and records the overshoot.

The model is never told the rule exists. Arm F is generated from arm C by script, so a hand edit
cannot introduce a quiet second difference.

### Why K = 3, when the historical rule said K = 1

Gen54's replay found every tested K met every criterion, so the frozen selection rule — take the
smallest — mechanically named K = 1. That was not used. Going from K = 10 to K = 1 raises firings
from 7 to 31 while total downstream work moves only from 1,396 to 1,449 tool calls: the extra
firings save about three calls each, on runs that had already finished. That spends the whole margin
between "quiet" and "finished" for nothing. K = 3 is also the value already exposed live, so this
generation changes the repaired semantics and measurement rather than changing patience at the same
time. This is a deliberate deviation, labelled as one, decided before any Gen55 result existed.

## What was proven before anything ran

Ten gates, no model, no GPU, no network.

| Gate | Result |
| --- | --- |
| HEAD is the frozen base | pass |
| arm C matches the Gen48 freeze | `205279d9…` |
| arm F regenerates deterministically | pass |
| running the tests alone does not move the tracked digest | pass |
| a real edit, and a new source file, both do move it | pass |
| an exact revert returns it to the initial digest | pass |
| **a reverted tree is never eligible** — five idle calls, zero aborts | pass |
| repeated same-tree passes count as idle | pass |
| K is 3, and the stop fires only after three idle completions | pass |
| the initial digest is captured before the first tool action | pass |
| the snapshot is written on every tool result | pass |
| retention failure injection still fails closed | pass |
| the archive is outside the repo and worktrees, unreferenced by either arm | pass |
| C and F compose byte-identical first requests on all four tasks | IP1 1,351 B, IP2 1,259 B, IP3 1,275 B, IP4 1,159 B |
| model, server binary, sampling and timeout match Gen52 | pass |

The seventh row is the Gen52 defect proven dead inside the real extension rather than in a Python
mirror. A live smoke on a throwaway fixture then confirmed arm F actually ends a Pi run: triggered
at tool call 7 with the idle count at 3, one same-batch overshoot recorded rather than a running
tool killed.

## Ruler and order

Gen48's frozen intent-persistence tasks IP1–IP4, byte-for-byte, with their hidden verifiers
untouched. 24 runs: 4 tasks × 3 stochastic samples × 2 arms. The order is **Gen52's own committed
manifest**, with arm F standing exactly where arm E stood — no new seed drawn — so the two
generations are directly comparable. Serial, fresh worktree and fresh Pi session per run.

No shared model seed exists, so a C run and its F partner are adjacent samples, not matched
reproductions.

## What happened

24 runs, 12 per arm, no crashes, no orchestration failures.

| | arm C | arm F |
| --- | --- | --- |
| hidden verifier passed | 10 / 12 | 7 / 12 |
| ended by the model | 9 | 10 |
| ended by the stop rule | 0 | **2** |
| **timed out** | **3** | **0** |
| current-tree receipt in hand at the end | 12 / 12 | 12 / 12 |
| median provider requests | 7.5 | 7.5 |
| median tool calls | 10.5 | 10.5 |
| **total tool calls** | **709** | **132** |
| median wall seconds | 42.4 | 41.7 |
| **total wall seconds** | **3,108** | **516** |

Nine of twelve pairs agreed on the verifier. The first composed request is byte-identical across
arms on every task, so the model could not tell them apart.

### The controller behaved exactly as frozen

Ten of twelve F runs became eligible. **Two triggered.** Both triggers satisfied every frozen
condition independently checked: at least one real mutation, a receipt bound to the current tracked
tree, the tracked tree differing from its initial value, an idle count of exactly 3, the last
visible check passing, the effective stop at or after the trigger, and zero same-batch overshoot.

**Zero stops on a tree equal to its start.** That was the hard-failure condition, and it is the
defect that made Gen52's version unusable.

**No contract violations of any kind.**

### The stall the controller was built for is real and recurrent

All three arm C timeouts are the same shape: the agent finishes, then re-runs its passing check
until the clock kills it.

| run | verifier | tool calls | exact repeats | redundant checks |
| --- | --- | --- | --- | --- |
| `IP3-r1-C` | passed | 291 | 279 | 279 |
| `IP1-r3-C` | passed | 160 | 148 | 142 |
| `IP1-r2-C` | failed | 161 | 149 | 144 |

Two of the three ended holding a **correct** tree. They were finished and could not tell. That is
2,700 seconds of GPU time spent on work that was already done, in the untreated arm, in one
generation.

Arm F had **no** timeouts.

### The decisive pair

`IP1-r2` is the slot that in Gen52 ran its passing test **144 times** and burned 900 seconds under
the first version of the rule.

- arm C: timed out at 900 seconds, 161 tool calls, 149 exact repeats, wrong tree.
- arm F: **stopped at 83 seconds, 16 tool calls, same wrong tree.**

The F run recorded `same_tree_passes_counted_idle: 1` — a repeated pass on the unchanged tree was
counted as idle instead of re-arming the receipt. Under the old rule that single event would have
reset the counter and the run would have looped again. This is change B working live, on the exact
trajectory that defeated its predecessor.

Same outcome, a tenth of the cost. The 817 seconds arm C spent bought nothing.

## Reading the verifier numbers honestly

Arm F passed 7 of 12 against arm C's 10 of 12, and that gap must not be read as a treatment effect.

**Ten of F's twelve runs never triggered.** In those runs a dormant rule changes nothing and F *is*
C. Three of F's five failures are in that group, including two where the rule never even became
eligible. They are sampling differences with no mechanical path to the intervention.

That leaves two triggered runs, and they differ:

- `IP1-r2-F` stopped on a wrong tree — and its C partner also failed, after 900 seconds. Nothing was
  lost.
- `IP1-r1-F` stopped on a wrong tree at 19 calls where its C partner reached a correct tree at 27.
  **This is the one run where the stop may have cost correctness, and that is not knowable from a
  live arm.** No claim is made either way.

So the honest count is: one candidate case, unknowable, out of 24 runs.

Both triggers are recorded as `live_stop_wrong_tree`. That is a fast-failure diagnostic, not
evidence the controller caused a wrong implementation: in each case the tree was already wrong when
the receipt was earned.

## Preregistered questions, answered

1. **Does F trigger, and legally?** Twice, and both triggers satisfied every frozen condition.
2. **Any revert defect?** None. Zero stops on a tree equal to its start; two F runs correctly never
   became eligible at all.
3. **Any repeated-check starvation?** None. A repeated same-tree pass advanced the idle count, and
   the decisive run stopped because of it.
4. **Runaways and downstream work?** Three in C, none in F. C spent 709 tool calls and 3,108 seconds
   against F's 132 and 516; the difference is almost entirely the three C timeouts.
5. **Stops on a wrong tree?** Two, both fast failures, one with a passing C partner.
6. **Stops on an unchanged tree?** Zero. Hard condition met.
7. **Treatment exposure?** 2 of 12. Low, and reported as the headline rather than buried.
8. **New blind spot?** None observed in these 24 runs.

## What this means

The controller is mechanically correct live: it fires only when its frozen conditions hold, it
refuses the case that broke its predecessor, it counts a repeated check as silence, and it never
kills a running tool. The failure mode it targets occurred three times in twelve untreated runs and
cost 2,700 seconds.

What this generation does not establish is a task-success benefit, and it was never expected to.
With two exposures, no efficacy claim is available, and the one run where a stop might have cost a
correct outcome cannot be resolved live.

On this evidence quiescent completion is worth having as an **optional harness guardrail** with its
limits stated: it improves termination, not correctness; it stops fast on wrong trees as readily as
right ones; and its benefit is concentrated in the minority of runs that stall.

## Evidence and operations

All 24 raw provider streams finalized through `raw-evidence-retention-v1` into a durable archive
outside the repository: **24 streams, 73,080,123 bytes, all digests matching, `retention_verified`
checked after the in-repo captures were removed.** Not committed.

Runtime: arm C 3,108 seconds, arm F 516 seconds, 3,624 seconds total — about 60 minutes of
GPU-attached execution, of which 2,700 seconds is the three untreated timeouts.

Artifacts: `results/pi_quiescent_completion_gen55/{preflight,aggregate,pairs,stop_and_safety_table,raw_stream_manifest}.json`,
`extensions/pi_state_control/pi_pilot_quiescent_tracked.ts`, `tests/test_gen55_live.py`.
