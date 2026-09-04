# Gen52 — teaching a run to notice it has finished

Evidence class: `architecture_quiescent_completion_ablation_paired_live`.
Base commit `a38da3b`. 24 live runs on the local Strix Halo, under Brian's standing GPU
authorization. Runtime is reported at the end, as agreed.

## The story so far, in plain words

Three generations in a row we changed what the agent could *see* and measured what happened. One of
those changes helped a lot, one did nothing, and the audit in Gen50 then explained why: across five
failed runs, not one failed because information was missing. Two of them had finished the job and
simply could not tell. One made its correct fix at tool call 314 of 584 and then made 269 more calls
that changed nothing. Another made its fix at call 6 of 442.

So the problem worth attacking was not memory. It was knowing when to stop.

Gen51 wrote that idea down as a rule anyone can check — *if the project's own tests passed, and
nothing has changed since, and three more actions have gone by without changing anything, the run is
done* — and replayed it over all 48 recorded runs from Gen47 and Gen49. On that historical evidence
the rule would have ended all five runaway runs at the right moment and would not have stopped any
of the five runs that were wrong. K = 3 was the earliest count that never cut a run short.

Gen52 is the first time that rule has been allowed to actually stop anything. This is the honest
test: a rule that looks good on the runs it was calibrated against has to be tried on new ones.

## What was changed

One thing, and only one. Arm E is arm C plus the stop rule.

Arm C is the harness-maintained state and control treatment, unchanged since Gen47 — the file's
hash is still `205279d9…`, the same one Gen48 froze. Arm E is generated from it by a script, so a
hand-edit cannot introduce a quiet second difference. The generator makes three documented inserts
and nothing else.

The model is not told any of this. There is no new instruction, field, tool or token; the stop rule
watches the ordinary tool stream and, when it fires, ends the run from outside. If it never fires,
arm E is arm C.

### The rule, exactly — `quiescent-completion-toolcall-k3-v1`

- the run must have changed at least one file;
- the most recent recognized visible check must have **passed**, on the current tree;
- nothing may have changed the tree since;
- a later failing visible check clears eligibility until another check passes;
- then three more ordinary tool completions with the tree unchanged, and the run ends as
  `quiescent_stop`.

The recognizer is the one `harness-state-v1` already uses, reused unchanged, with the same
exclusions that keep the hidden verifier from ever counting as a check. The hidden verifier is not
an input to the rule at any point; it is read afterwards, to score what the rule did.

K is counted in **tool calls**, not provider requests. Gen51's replay had to make that substitution
because the logs do not order the two together, and Gen52 implements the same unit the calibration
actually used rather than quietly translating it back.

### The one thing the rule refuses to do

It never kills a tool that is still running. If the third qualifying completion arrives while other
calls from the same batch are still outstanding, the stop waits for the batch to drain and records
the overshoot instead of hiding it.

## What was tested before anything ran

No model, no GPU, no network. If any of these had failed, the generation would have stopped before
the first task request rather than being repaired afterwards.

| Gate | Result |
| --- | --- |
| arm C byte-identical to the frozen Gen48 treatment | `205279d9…`, unchanged |
| arm E generated from arm C, reproducibly | pass |
| K = 1 and K = 2 do not stop; K = 3 stops | pass |
| a mutation after the passing check resets the count | pass |
| a failing visible check clears eligibility | pass |
| a check that passes before any mutation is ineligible | pass |
| a new passing check after a later mutation re-arms | pass |
| the hidden verifier is not recognized as a visible check | pass |
| the stop waits for an in-flight batch and records the overshoot | pass |
| C and E compose byte-identical context | pass |
| raw-evidence retention failure injection (delete, tamper) fails closed | pass |
| model, server binary, sampling and timeout match the frozen identity | pass |
| local endpoint only | pass |

The probe earned its keep by failing first. Writing the harness's own log files inside the worktree
changes the tree digest on every tool result, which silently voids every receipt and means the rule
can never fire. Production already keeps those files outside the worktree; the probe did not, and
the failure was loud rather than a permanent quiet no-op.

A live smoke on a throwaway fixture then proved the one thing a synthetic probe cannot: that a real
Pi run actually ends when the policy aborts it, cleanly and with its evidence intact. Arm E stopped
at tool call 6 with the count at 3, exit code 0; arm C ran on to 7 tool calls.

## The ruler and the run order

The tasks are Gen48's frozen `intent-persistence-v1` IP1-IP4, byte-for-byte, with the same hidden
verifiers. No new ruler was made for this generation. This is the most recent ruler on which arm C
already produced both ordinary completions and runaway trajectories, so it can show a benefit and
the main safety risk on the same runs.

24 runs: 4 tasks × 3 stochastic samples × 2 arms, in an order frozen from seed `20260909` before the
first request, with C and E adjacent inside each pair and the leading arm alternating. Serial, one
inference stream at a time, a fresh worktree and a fresh Pi session per run.

There is no shared model seed, so a C run and its E partner are adjacent samples, not matched
reproductions of the same randomness.

## Evidence retention

Every raw provider stream is finalized through `raw-evidence-retention-v1` into a durable archive
outside the repository and outside every ephemeral area, and the whole manifest is re-verified after
all runs and after cleanup. This is the contract Gen51 built because the Gen47 and Gen49 streams
were deleted by the script that hashed them. The streams are retained locally and are not committed.

## What happened

24 runs, 12 per arm, no crashes, no orchestration failures.

| | arm C | arm E |
| --- | --- | --- |
| hidden verifier passed | 11 / 12 | 8 / 12 |
| ended by the model | 12 | 10 |
| ended by the stop rule | 0 | 1 |
| timed out | 0 | 1 |
| current-tree receipt in hand at the end | 10 / 12 | 12 / 12 |
| median provider requests | 7 | 6.5 |
| median provider payload bytes | 82,659 | 78,971 |
| median tool calls | 10 | 9.5 |
| total tool calls | 132 | 270 |
| median wall seconds | 38.5 | 39.4 |
| total wall seconds | 569 | 1,349 |

Seven of the twelve pairs agreed on the verifier. The first composed request of every run is
byte-identical across arms within each task, which is H1 checked on live data rather than only on
the probe.

The stop rule became eligible in 10 of 12 E runs and fired in **one**.

### The rule is not what made arm E score worse

Arm E failed four runs to arm C's one, and that difference is worth reading carefully rather than
quickly. Three of E's four failures had **no trigger at all**: in those runs arm E is arm C, because
a dormant policy that never fires changes nothing. Only `11-IP1-r1-E` involved the intervention.

The remaining difference is 12 adjacent stochastic samples per arm with no shared model seed. Arm C
failed `IP1-r3` where arm E passed it. A three-run gap on this ruler is not something this design
can separate from sampling.

### The one stop that fired, in full

`11-IP1-r1-E` is worth stating as a story, because the counter alone hides it.

IP1 ships a test that still encodes the **old** firmware ratio. The agent made the correct fix —
`STEPS_PER_MM = 8` with a separate `TELEMETRY_STEPS_PER_MM = 4` — and the project's own tests
**failed**, because they expect the old value. So it reverted its own correct fix back to
`STEPS_PER_MM = 4`, the stale test passed, and it earned a receipt. Three ordinary calls later the
rule ended the run.

The tree it stopped on is byte-identical to the tree it started with. Net progress: nil.

Everything the rule promised, it delivered: the receipt was valid, the tree was unchanged between
receipt and stop, no in-flight tool was killed, overshoot zero. The defect is in the specification.
Eligibility asks that *a mutation happened*, not that *the tree actually changed*, so a run that
mutates and undoes itself qualifies. This is recorded as `stopped_on_a_tree_identical_to_the_start`,
separately from the plain wrong-tree count, because folding the two together would hide it.

Whether that run would have recovered had it continued is **not knowable** from a live arm, and is
not claimed here. Its arm C partner did pass, using 26 tool calls to arm E's 16.

### The finding that matters most: the rule is blind to the loop it was built for

`23-IP1-r2-E` ran the **same passing pytest command 144 times in a row on an unchanged tree** and
timed out at 900 seconds after 163 tool calls. The stop rule never fired.

The reason is in the rule as written. A passing check re-arms the receipt and resets the count, so
the K ordinary completions never accumulate. A run that idles by re-running the check that already
passed — which is a very natural way for an agent to stall once it believes it is done — is exactly
the shape this rule cannot see.

This is what the out-of-sample test was for. Gen51's offline replay contains the same blind spot,
and 48 historical runs could not reveal it, because none of them looped on the check itself. The
calibration was clean and the rule still had a hole in it.

Per the frozen brief, nothing was tuned after exposure: K stays 3, the rule is unchanged, and this
is reported as the result rather than repaired into a better-looking one.

One evidence gap follows from it. A timed-out run is killed before the extension writes its final
stop summary, so `quiescent_stop.json` is absent for `23-IP1-r2-E` and its eligibility fields read
`null`. The derivation stream is complete and the loop is fully reconstructable from it, but the
summary itself is missing, and a future runner should write that file on every tool result rather
than only at a stop or a clean shutdown.

## Preregistered hypotheses, answered

**H1 integrity — held.** C and E compose byte-identical context, proven on synthetic traces before
exposure and on the first request of every live run. Arm C's file hash is unchanged from Gen48.

**H2 efficiency — not demonstrated.** Medians are indistinguishable (9.5 against 10 tool calls, 39.4
against 38.5 seconds). Arm E's larger totals come entirely from the one timeout the rule failed to
catch. The rule did not reduce runaway behaviour on this generation, because the single runaway that
occurred was of a shape it cannot see.

**H3 correctness — as expected, no improvement.** 8/12 against 11/12, with only one of the four
failures involving the intervention.

**H4 safety — one adverse case, and it is instructive.** `live_stop_wrong_tree = 1`. The receipt was
valid for what the visible check covered and silent about the requirement it never checked. Worse
than that: the run had undone its own correct work first. This is real evidence against treating a
visible receipt as a completion guarantee.

**H5 null — partly.** Only one new trajectory entered a runaway state, and it was invisible to the
rule. No K was changed, no repetitions added, no friendlier ruler built.

**H6.** Nothing here supports memory, retrieval or larger context. What it supports is that
deterministic termination is harder to specify than it looks.

**H7.** Retrieval stays deferred.

## Evidence and operations

All 24 raw provider streams were finalized through `raw-evidence-retention-v1` into a durable
archive outside the repository, the in-repo capture copies were removed only after the archive was
verified, and the archive was re-read afterwards: **24 streams, 59,097,996 bytes, all digests
matching, `retention_verified: true` checked after cleanup.** This is the first generation whose raw
model output survives by contract rather than by accident. The streams are retained locally and are
not committed.

Runtime: arm C 569 seconds, arm E 1,349 seconds, 1,918 seconds total — about 32 minutes of
GPU-attached execution. Arm E's figure is dominated by its single 900-second timeout; the medians
are 39.4 seconds against 38.5.

## What I would do next, not executed

Fix the rule's definition of quiescence before spending any more GPU time on it. Two changes fall
straight out of this generation, and both are cheap to check offline against the 48 historical runs
plus these 24:

1. **Count the repeated qualifying check as an idle action, not as a re-arm.** A check that passes
   again on a tree that has not changed is new evidence of nothing. Re-arm only when the tree has
   changed since the receipt.
2. **Require a net tree change, not merely that a mutation occurred.** A run whose tree is back
   where it started has not finished; it has gone in a circle.

Both are testable with no model, which is where they belong. I would not run another live arm until
the offline replay over 72 runs shows the revised rule catches `23-IP1-r2` and declines to stop
`11-IP1-r1`.

What I would not do is treat the 8/12 against 11/12 as evidence about the intervention. Three of
those four failures never met the treatment.
