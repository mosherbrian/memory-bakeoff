# Harness-maintained state and control: the Gen47 ablation, frozen

**Evidence class:** `architecture_state_control_ablation_design_no_score`. No model, no GPU, no
network. Synthetic event logs only.

Gen45 produced a negative result for the model-maintained arm, but it also showed *why* the result
cannot be read as a test of the architecture: across all twelve runs the control layer accepted
**0 transitions**, reached the completion
gate 0 times, and every run ended in phase
`inspect`. The model did not adopt the three tools, so there was no control loop to evaluate.

Gen46 removes that dependency and freezes the arm that tests the architecture's actual claim.

## The change, and only this change

Arm **C** `pi_harness_state_control_v1` keeps arm B's composer, caps, history treatment and
compaction handling **exactly**, and changes one thing: the state and the phase are derived by the
harness from ordinary visible tool events instead of waiting for the model to call unfamiliar
tools. C does not offer the three state/control tools at all — their non-adoption is the mechanism
being removed, so keeping them for symmetry would defeat the point.

Deliberately **not** changed, and recorded as deferred rather than quietly folded in:
`persistent_task_prompt_floor`, `on_demand_history_retrieval`, `larger_recent_window`. The task-prompt
floor is a real suspect from Gen45 and it stays a separate experiment.

## The derivation contract, `harness-state-v1`

The line this design will not cross is semantic interpretation. It records what was observed —
files read, the repository changed, a visible check run and its exit status — and never what any of
it means. No inferred cause, no plan, no next action. If a field would need a model to fill it in,
it is not in the state.

| from | automatic next |
| --- | --- |
| `blocked` | `inspect`, `plan`, `implement`, `validate` |
| `done` | `implement` |
| `implement` | `validate`, `plan`, `blocked` |
| `inspect` | `plan`, `implement`, `blocked` |
| `plan` | `implement`, `inspect`, `blocked` |
| `validate` | `done`, `implement`, `blocked` |

Rules: two inspection calls leave `inspect`; the first repository mutation enters `implement`; a
recognised visible check after a mutation enters `validate`; a failed check returns to `implement`;
a mutation after a passing check **invalidates the receipt** and returns to `implement`; `done` is
recorded only if a passing receipt still matches the current tree digest at session end.

Validation commands are classified by a frozen pattern family drawn from the fixtures' own public
tooling — pytest, unittest, `run_checks.py` — and the hidden verifier is excluded by name in
`FORBIDDEN_IN_VALIDATION`, so a run that invokes it gets no receipt at all.

State is bounded exactly as before: 4,096 bytes, the last
6 files read or modified, the last 6
objective checkpoints, which may only be one of
`repository_mutated`, `validation_failed`, `validation_passed`.

## Preflight

| check | result |
| --- | --- |
| arm b unchanged | identical=true |
| bounded and restartable | restart_matches=true, within_cap=true |
| composer unchanged | matches_gen44=true |
| control loop runs | reached_done_from_a_valid_receipt=true |
| deterministic replay | identical_across_replays=true, identical_after_shuffling_nothing=true |
| hidden verifier is not a receipt | classified_as_validation=false, ordinary_check_still_classified=true, valid_receipt_at_end=false |
| illegal transition fails closed | phase_unchanged=true, recorded_as_rejected=true |
| no hidden data access | imports_nothing_from_the_benchmark=true, no_gold_or_answer_token_in_code=true, opens_no_file_but_its_own_hash=true, verifier_never_appears_in_logic=true |
| no network | outbound_blocked=true |
| python typescript equivalence | summaries_identical=true, typescript_available=true |
| receipt invalidation | phase_returned_to_implement=true, valid_receipt_at_end=false |

The control loop the model never drove now runs on its own: on the ordinary synthetic trace the
phase path is **inspect → plan → implement → validate → implement → validate → done**, 6 transitions accepted,
ending with a receipt valid for the current tree.

Three results are worth naming individually.

**Receipt invalidation works.** A passing check followed by another edit produces one receipt, one
invalidation, no valid receipt at the end, and a return to `implement`. Artifacts still outrank
state, and now they do so without the model's cooperation.

**The hidden verifier cannot become a receipt.** `python ../verifier.py` is not classified as a
validation command, produces no receipt, and leaves the phase in `implement`, while
`python -m pytest` is classified normally.

**The Python contract and the TypeScript arm agree byte for byte.** The same synthetic event log
replayed through `harness_state.py` and through the extension that will actually run in Gen47
produces identical summaries. That is the check that stops the frozen contract and the live code
drifting apart between generations.

Arm B is untouched: its extension still hashes to the value Gen45 recorded
(`64af44bfc24969ab…`).

## What Gen47 would run

24 runs, pi_state_control_v1 against pi_harness_state_control_v1, on the same frozen T1–T4
tasks, three stochastic samples per cell, serial, fresh worktree and session each time, at the
Gen45 model identity and sampling. A **new** order seed, 20260906, because reusing Gen45's
ordering would not be randomisation. Same 900 s timeout, same retry policy, same hidden verifier,
plus direct adoption metrics: for B, each tool offered, called, accepted, rejected and its
first-call turn; for C, harness-derived updates, automatic transitions, receipts and invalidations
with their source events.

Gen47 needs Brian's authorization again. Gen45's does not carry over.

## What this can and cannot show

If C exercises the loop on every run — which the preflight says it will, because it is event-driven
— then a difference between B and C is about *maintenance of state*, not about whether the model
volunteers to maintain it. If C still fails T2 and T3 the way B did, the bounded composer becomes
the leading suspect and the deferred task-prompt floor gets its own experiment.

What it cannot show is which part of the bundle did the work. C changes maintenance and removes
three tools at once. That is stated here rather than discovered later.

Contract `src/memory_bakeoff/pi_state_control/harness_state.py`, sha256
`2b3acdb27b9b43a4316d84542ca79421fd739d69e2c30fdfa2421037d1b0b165`. Design digest `202115b4b71b3f5578408dcd66cec3020d218b256b625310a13804870afc48b1`.
