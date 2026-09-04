# Gen54 — the fingerprint was measuring the wrong thing

Evidence class: `architecture_quiescent_completion_tracked_digest_offline_replay_no_score`.
Base commit `f0c4d80`. No model, no GPU, no network, no live arm.

## The story, in plain words

We are teaching an automated coding agent to notice when it has finished, so it stops instead of
grinding on work that is already done. The rule looks only at things anyone can see: the project's
own tests passed, nothing has changed since, and a few more actions have gone by without changing
anything.

Two generations ago we let that rule stop runs for real, and it stopped one that had quietly undone
its own work. The agent had made the correct fix; the project's own out-of-date test rejected it, so
the agent put the old value back, the stale test went green, and the rule ended the run on a codebase
identical to the one it started with.

Last generation we added a rule that was supposed to catch exactly that: *a codebase back where it
started is not finished*. It never fired. This generation found out why, and it is almost silly.

**The way we fingerprint "the codebase" included files that running the tests creates.** Python
leaves compiled bytecode behind, and our fingerprint counted it. So merely running the tests changed
the fingerprint, and the run that had reverted itself still looked like it had changed something.
The new safety rule was asking a real question against a measurement that could not answer it.

Gen54 changes the fingerprint to ignore what running the tests leaves behind, while still noticing a
genuinely new file. Then it replays the rule over all 72 recorded runs again — but this time it
rebuilds each run's codebase from that run's own recorded edits, so the fingerprint reflects the
project rather than its build output.

**The result is clean.** The run that reverted itself is now refused at every patience setting, for
the right reason: its codebase really is back where it started. The run that stalled by re-running
its passing test 144 times is still caught, about 21 actions in instead of 163. Across all 72 runs
and every patience setting, no run is stopped while it is still making progress, and the count of
runs stopped on an unchanged codebase is zero.

That was the condition set for going live. It is met.

## What changed

Only the measurement. The rule is `quiescent-completion-toolcall-v2`, unchanged from Gen53.

`tracked-tree-digest-v1`, contract sha256 `2629cd24f608b7d2…`: the same temporary-index digest as
before, with a frozen list of build artifacts excluded — `__pycache__`, `*.pyc`, `.pytest_cache`.

The obvious alternative, fingerprinting only files the project already tracks, was rejected: it
would go blind to a newly added source file, and adding a module is real progress. Excluding named
artifacts keeps new files visible.

Proven on a scratch repository:

| step | old fingerprint | `tracked-tree-digest-v1` |
| --- | --- | --- |
| start | `69fdb14c` | `8bfda02a` |
| after running the tests | changed | **unchanged** |
| after a real edit | changed | changed |
| after reverting that edit | ≠ start | **= start** |
| after adding a new source file | changed | changed |

And proven again through the generated arm itself, driving the real extension rather than the Python
mirror: an edit moves the digest, a revert returns it exactly, the tests do not move it, and
`net_tree_changed` reads false on a reverted tree.

## The run that forced this, reconstructed

`11-IP1-r1-E` is the run v1 stopped. Its two edits are recorded verbatim, so they were replayed onto
a fresh copy of the frozen IP1 fixture, with both fingerprints computed at every step. Both applied
cleanly; none skipped.

| step | old fingerprint | `tracked-tree-digest-v1` |
| --- | --- | --- |
| initial | `732a4b97` | `732a4b97` |
| after the correct fix | `df099f72` | `df099f72` |
| after the agent reverted it | `732a4b97` | `732a4b97` |
| after running the visible tests | **`ed00c99a`** | **`732a4b97`** |

The last row is the entire defect. The old fingerprint was knocked off the starting value by running
the tests, and that is what made a reverted run look changed.

## The replay, over all 72 recorded runs

Gen47 (24), Gen49 (24), Gen52 (24). Each run's tree rebuilt from its own recorded edits on a fresh
fixture copy. 71 of 72 fully reconstructable; `08-T4-r1-B` has one edit whose recorded text could not
be applied exactly and is reported rather than guessed at.

| K | fires | truncates observed progress | stops a wrong tree | runaways caught | stopped on a tree equal to its start | downstream tool calls |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 31 | 0 | 1 | 6 / 6 | **0** | 1,473 |
| 2 | 15 | 0 | 1 | 6 / 6 | **0** | 1,458 |
| 3 | 9 | 0 | 1 | 6 / 6 | **0** | 1,449 |
| 5 | 8 | 0 | 1 | 6 / 6 | **0** | 1,433 |
| 10 | 7 | 0 | 1 | 6 / 6 | **0** | 1,396 |

The last column but one is the number Gen53 said a corrected fingerprint would drive to zero. It is
zero at every K.

**`11-IP1-r1-E`: refused at every K**, with `became_eligible` false — not merely unreached. That is
the difference between passing this test and passing it by luck, and it is what Gen53 could not
achieve.

**`23-IP1-r2-E`: caught at every K**, at tool index 21 to 30 of a run that reached 163 calls before
timing out. Its hidden verifier failed, so it counts as a wrong-tree stop at every K. Stopping it
does not make it correct; it turns a fifteen-minute timeout into a fast failure.

## Which K, and a flagged deviation

The frozen decision rule says: recommend the smallest tested K meeting every criterion. Every K
meets every criterion, so the mechanical answer is **K = 1**, and the artifact says so.

**I recommend K = 3 instead, and I am flagging that as a deviation rather than quietly substituting
it.** The reason is in the table. Going from K = 10 to K = 1 raises firings from 7 to 31 while total
downstream work moves from 1,396 to 1,473 tool calls — the 24 extra firings save about three calls
each, on runs that had already finished. That is no benefit, and it spends the entire margin between
"the tree has been quiet" and "the tree is finished" on nothing. K = 3 is also the value already
exercised live in Gen52, so choosing it changes one thing at a time.

If the planner prefers the frozen rule as written, K = 1 is supported by this evidence and I will
not argue further.

## What this proves and does not

It proves the fingerprint was the defect, that correcting it makes the revert refusal real, and that
the correction costs nothing on any recorded trajectory.

It does not prove the rule is safe live. This is an offline replay over trajectories produced under
different policies, and Gen52 already demonstrated that a clean historical screen can miss a natural
out-of-sample shape — that is precisely how the repeated-check loop got through. A live arm remains
the only way to find the next one.

Nothing here revives retrieval, a prompt floor, a larger window or semantic memory.

## Evidence

Gen52's retained archive was re-verified and not modified. Gen54 ran no model and produced no new
provider stream. The Gen47 and Gen49 stream loss remains recorded as lost.

Artifacts: `results/pi_quiescent_completion_gen54/{focal_run_reconstruction,replay_72_runs_tracked_digest}.json`,
`src/memory_bakeoff/pi_state_control/tracked_digest.py`,
`extensions/pi_state_control/pi_pilot_quiescent_tracked.ts`,
`tests/test_gen54_tracked_digest.py`.
