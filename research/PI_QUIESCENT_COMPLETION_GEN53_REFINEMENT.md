# Gen53 — one of the two repairs worked, and the other never got the chance

Evidence class: `architecture_quiescent_completion_refinement_offline_replay_no_score`.
Base commit `c0dfccf`. No model, no GPU, no network, no new runs, no live arm.

## The story, in plain words

We have been trying to teach an automated coding agent to notice when it has finished, so it stops
instead of grinding away for fifteen minutes on work that is already done.

The rule we settled on is deliberately simple and checks only things anyone can see: *the project's
own tests passed, nothing has changed since, and three more actions have gone by without changing
anything — so stop.* We calibrated it against 48 recorded runs, where it looked clean. Then last
generation we let it actually stop runs, and it failed twice, in two different ways.

One run made the correct fix. The project's own test was out of date and rejected that correct fix,
so the agent put the old value back, the stale test went green, and our rule stopped the run — on a
codebase byte-for-byte identical to the one it started with. It had asked only whether *an edit
happened*, never whether *anything had actually changed*.

The other run ran the same passing test 144 times in a row and timed out. Every pass made the rule
think there was fresh news, resetting its patience counter, so the exact stall it was built to catch
could never build up three quiet actions.

Gen53 made two repairs and replayed the repaired rule over every run we have on record — 72 of them,
from three generations — without running the model at all.

**The second repair works.** Treating a repeated pass on an unchanged codebase as *silence* rather
than *news* catches the 144-repeat run at every patience setting we tested, roughly 25 actions in
instead of 163, and it catches all six recorded runaway runs across all three generations. It never
cuts short a run that went on to do more work.

**The first repair does not, and the reason is worth knowing.** We told the rule "a codebase that is
back where it started is not finished". But the fingerprint we use for "the codebase" is taken over
the whole working folder, and *running the tests writes files* — Python leaves compiled bytecode
behind. So the run that reverted itself still looked changed, because of bytecode. The new check
never engaged. It appears to pass at the two most patient settings only because that run ran out of
actions first, which is luck, not a fix.

**So the recommendation is: do not run another live test yet.** One of the two defects is repaired
and measured. The other needs the codebase fingerprint to ignore files the project itself does not
track. That is a small change, but it is a third change to a rule that is currently frozen, and this
generation was explicitly scoped to two. It belongs in the next frozen brief, not in a quiet patch
here.

Everything below is the detail behind those four paragraphs.

## What changed

`quiescent-completion-toolcall-v2`, contract sha256 `e37d6b4a76941a75…`, frozen before any replay
outcome was inspected. Exactly two semantic changes from v1:

- **A. Net-tree-change eligibility.** The initial tree digest is recorded before the agent's first
  action. The rule is ineligible whenever the current digest equals the initial one, however many
  mutation events occurred. At least one mutation is still required; this is additional.
- **B. A same-tree pass is idle, not a re-arm.** A pass creates a receipt only when no valid receipt
  exists for the current tree. While a receipt is valid and the tree is unchanged, a later pass —
  even under a different command — increments the idle count instead of resetting it. A fail still
  invalidates; a mutation still invalidates; after either, a later pass may create a new receipt.

Unchanged: the recognizer, the hidden-verifier exclusions, the safe-stop boundary that never kills a
running tool, and K counted in tool calls.

### One correction found while building it

The first draft captured the initial tree digest at the first tool *result*. That is too late: if
the first action is a mutation, the "initial" tree is already the mutated one and a later revert to
the real starting point goes unnoticed. It is now taken at arm startup, before any tool runs, and
the Python rule raises rather than guessing if a caller fails to set it. The abrupt-termination test
below is what exposed this.

## Part A — the evidence gap Gen52 left

Gen52's one timeout was killed before the extension wrote its stop summary, so that run's
eligibility fields read `null` despite a complete derivation stream. The v2 arm now writes the
quiescence snapshot on **every tool result**, staged and atomically renamed.

Tested by SIGKILL — the harshest termination available — part way through a run:

| Property | Result |
| --- | --- |
| snapshot exists after SIGKILL | yes |
| parses as JSON | yes |
| internally consistent | yes |
| initial tree recorded before the first action | yes, differs from current |
| no partial files left behind | yes |
| fields present | contract, k, initial/current tree digest, net-tree-changed, receipt identity and tree, idle count, eligibility, last visible-check outcome, mutations, trigger/effective-stop indices, overshoot, tool index |

Gen52's missing summary is **not** reconstructed after the fact. That evidence stays as recorded.

The v1 arm file is untouched, because its hash is Gen52's recorded evidence. v2 is a new file,
generated from arm C by script, three documented inserts.

## Part B — the contract, proven on synthetic traces before any replay was read

Twelve scenarios, all passing:

| Scenario | Expected | Result |
| --- | --- | --- |
| mutate → pass → 3 idle | fires at K=3 | pass |
| mutate → pass → 3 repeated passes on the same tree | fires at K=3 | pass |
| the same, under a *different* check command | fires at K=3 | pass |
| mutate → pass → 1 repeat → 2 idle | fires at K=3 | pass |
| mutate → revert to the initial tree → pass → 12 idle | never eligible | pass |
| pass before any mutation | ineligible | pass |
| mutation after the receipt | invalidates and resets | pass |
| failing check after the receipt | invalidates and resets | pass |
| pass after a fail | re-arms | pass |
| tree A → pass → tree B → pass | counts fresh for B | pass |
| trigger reached mid-batch | waits for the batch, records overshoot | pass |
| hidden verifier command | not a visible check | pass |

The TypeScript arm and the Python rule were driven through the same ten traces and compared on stop
indices plus fourteen snapshot fields: **zero disagreements**.

## Part C — the replay over all 72 recorded live runs

Gen47 (24), Gen49 (24) and Gen52 (24). No outcome-based exclusions. Receipt provenance kept
explicit: Gen47 arm B is `offline_reconstructed_observable_receipt` because it never had harness
derivation; everything else uses authoritative harness validation records. Gen52's arm E records are
the **v1 live policy**; v2 here is a counterfactual and is never presented as having run.

| K | fires | truncates observed progress | stops a wrong tree | runaway runs caught | downstream tool calls | same-tree passes counted idle |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 32 | 0 | 2 | 6 / 6 | 1,729 | 2 |
| 2 | 16 | 0 | 2 | 6 / 6 | 1,718 | 3 |
| 3 | 14 | 0 | 2 | 6 / 6 | 1,702 | 5 |
| 5 | 8 | 0 | 1 | 6 / 6 | 1,672 | 7 |
| 10 | 7 | 0 | 1 | 6 / 6 | 1,630 | 17 |

**No K truncates observed progress on any fully observed trajectory.** All six recorded runaway
runs are caught at every K.

### The run v1 missed — `23-IP1-r2-E`, the 144-repeat loop

v2 catches it at every K, at tool index 23 through 32 of a run that reached 163 tool calls before
timing out, leaving 262 to 280 recorded tool calls downstream. Change B did exactly what it was
written to do.

Its hidden verifier failed, so this trigger counts as `would_stop_wrong_tree`. That is worth stating
plainly: stopping this run does not make it correct. It converts a fifteen-minute timeout into a
fast failure. An efficiency result, not a correctness one.

### The run v1 should not have stopped — `11-IP1-r1-E`

**v2 still triggers on it at K = 1, 2 and 3.**

The leaf records `start_tree` and `final_tree` as the same digest, `732a4b97` — the agent's revert
was exact and the tracked source ended where it began. But the digest recorded at the qualifying
check was `966c0910`, so `current != initial` was satisfied and the new predicate never engaged.

The cause is the digest itself. It is `git add -A` over the whole worktree, so it counts untracked
build artifacts, and running the visible tests creates `__pycache__` and `.pytest_cache`. **Running
the tests changes the fingerprint on its own.**

v2 declines at K = 5 and K = 10, but only because the run ran out of calls before accumulating five
idle actions. The criterion is met incidentally, not in substance, and it should not be counted as
change A working.

Because that run was actually stopped by v1, it has no post-stop trajectory. It is marked
`trajectory_censored_by_prior_live_stop`, its missing tail is not used as evidence of safety, and no
guess is made about what the agent would have done next.

## The Gen54 decision, answered against the frozen rule

| Criterion | K=1 | K=2 | K=3 | K=5 | K=10 |
| --- | --- | --- | --- | --- | --- |
| declines the revert-to-start stop | no | no | no | incidentally | incidentally |
| catches the repeated-check timeout | yes | yes | yes | yes | yes |
| catches the historical runaway shapes | yes | yes | yes | yes | yes |
| zero observed-progress truncation | yes | yes | yes | yes | yes |
| instrumentation not blocked | yes | yes | yes | yes | yes |

Read literally, K = 5 is the smallest K meeting every criterion, and the mechanical recommendation
in `replay_72_runs.json` says so. **I am not recommending it.** The first criterion is satisfied by
accident on one run, and a rule that passes a safety test by luck has not passed it. Proposing a
live arm on that basis would repeat exactly the Gen52 mistake: a clean-looking screen hiding a
defect the evidence could not show.

So, per the brief's instruction not to invent a third patch here: **reported, and stopped.**

What the next brief should decide, if Sol agrees it is worth it: whether the tree digest should
ignore content the project does not track. That is one line in the digest helper — seed the
temporary index from `HEAD` and add only tracked paths, or honour `.gitignore` — and it would make
change A measurable rather than inert. It is testable offline against these same 72 runs with no
model. Until then, change A is unproven, not disproven: it has never actually been exercised.

## What this does and does not prove

It proves change B fixes the starvation defect on every recorded trajectory, and that neither change
introduces observed-progress truncation at any tested K.

It does not prove change A works, because the recorded digests cannot exercise it. It is not a live
causal result: an offline replay says what a rule would have decided on trajectories produced under
a different policy, and Gen52 already demonstrated that a clean historical screen can miss a natural
out-of-sample shape.

Nothing here revives retrieval, a prompt floor, a larger window or semantic memory. Gen50's five
audited failures remain zero `missing_relevant_context`.

## Evidence

Gen52's retained archive was re-verified before any raw-stream-derived fact was used and was not
modified: 24 streams, `retention_verified: true`, no failures. Gen53 ran no model and produced no new
provider stream. The Gen47 and Gen49 stream loss remains recorded as lost.

Artifacts: `results/pi_quiescent_completion_gen53/{v2_contract,preflight,replay_72_runs}.json`,
`extensions/pi_state_control/pi_pilot_quiescent_v2.ts`,
`src/memory_bakeoff/pi_state_control/quiescent_v2.py`,
`tests/test_gen53_quiescent_v2.py`.
