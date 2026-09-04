# The human-direction floor: arm D, frozen

**Evidence class:** `architecture_human_direction_floor_ablation_design_no_score`. No model, no
GPU, no network. Synthetic transcripts and freshly built fixtures only.

Gen47 showed the bounded composer works once state is maintained for the model rather than by it.
The question left standing is narrower and worth asking on its own: should the **original human
instruction** stay addressable after the ordinary recent window has moved past it, or is it
transcript material like anything else?

In the architecture, human direction is a separate authority layer. This ablation asks whether
that authority deserves a floor.

## The arms

**C** `pi_harness_state_control_v1` — the Gen47 arm, unchanged, hash verified against the Gen47
record.

**D** `pi_harness_state_control_task_floor_v1` — arm C plus exactly one intervention. The original
first user message is captured verbatim by identity, and once the ordinary window rule would no
longer carry it, it rides on every later request as a `human_direction` field. No paraphrase, no
summary, no model-maintained goal, no extracted checklist.

D is **generated from C's source** by a script with one documented insert, so the two cannot drift
apart between generations. The floor field is appended last, which is what makes the pre-activation
views byte-identical rather than merely similar.

## The integrity property, proven

| turns | C carries the task | arms byte-identical | D floor active |
| --- | --- | --- | --- |
| 1 | yes | **yes** | no |
| 2 | yes | **yes** | no |
| 3 | no | no | **yes** |
| 10 | no | no | yes |
| 100 | no | no | yes |

Before activation the two arms compose byte-identical payloads. At the first request where C's
window no longer holds the task, D's floor turns on, adds
303 bytes, and never turns off. The prompt is still
verbatim at 100 turns. Both arms offer the same tool
surface — [] — and neither offers the Gen45 state/control tools.

## The ruler: intent-persistence-v1

T1–T4 are ceiling-limited for C at 12/12, so repeating them would mostly measure the cost of
repeating a prompt. These four tasks are built so the instruction still matters late.

| id | shape | frozen tree | prompt bytes | public requirements A / B |
| --- | --- | --- | --- | --- |
| IP1 | compatibility constraint stated only in the instruction | `732a4b97815b` | 339 | the new steps-per-millimetre ratio / telemetry steps unchanged for a given position |
| IP2 | negative constraint with a tempting local violation | `0d87ea1dcf52` | 247 | the new sailing and the None behaviour / as_list still returns a plain list of strings |
| IP3 | a second requirement that outlives the first fix | `de99e04fb9e6` | 263 | blank and missing holds ignored / summary is alphabetical |
| IP4 | the visible check is incomplete | `c769a25f3bab` | 147 | the upper bound is unchanged / negatives clamp to zero, which the visible test does not check |

- **IP1** — the telemetry constraint appears nowhere in the code or tests; it lives only in the user's instruction, and the obvious single-constant edit breaks it
- **IP2** — returning the list object itself, or a tuple, is the natural way to add a sailing; the instruction forbids changing what as_list returns
- **IP3** — the blank-hold fix is immediate and satisfying; the alphabetical ordering requirement is still true several edits later
- **IP4** — the shipped test only covers the upper bound, so a partial fix passes the project's own check while violating the instruction

Every task fails its hidden verifier initially and passes under a reference fix that exists only in
the builder. Each has **two named public requirements**, so a live failure can be reported as "A or
B" from the verifier's own subchecks rather than by anyone's judgement.

### The incomplete-visible-check diagnostic

IP4's shipped test covers only the upper bound. A plausible partial fix — replacing the bound with
`min(value, MAX_OPEN)` — **passes the project's own check** (1 passed in 0.00s) and **fails
the hidden verifier** (AssertionError: B: clamp(-5) -> -5, expected 0). That is proven here, before any model sees it.

It exists because Gen47's arm C reached control-valid `done` on all twelve runs and the gate has
never been observed disagreeing with task truth. The semantics are frozen now: `control_valid_done`
means a passing recognised **visible** check for the current tree, nothing more. If that holds
while the hidden verifier fails, the run is recorded as `visible_receipt_false_assurance` — an
artifact outranking state while still being incomplete evidence. That is a limit of artifact
authority, not a control failure, and the hidden result is never fed back into control.

### One property recorded rather than discovered later

IP1's shipped test encodes the **old** firmware ratio, so a correct fix makes it fail until the
agent updates it. That is realistic, and it means IP1 cannot reach control-valid `done` without
touching the visible test. Recorded here so nobody meets it as a surprise in the live run.

## Gen49, if authorised

24 runs, C against D, four tasks, three stochastic samples per cell, adjacent and counterbalanced
from a new seed 20260907, at the Gen47 model and sampling identity, 900 s timeout, exact
payload observer on both arms. Gen47's authorisation does not carry forward.

Measurements are frozen: hidden verifier pass/fail and its A/B subchecks, termination status and
`control_valid_done` reported separately, exact payload and message bytes, requests, tool calls and
the three churn definitions, plus floor activation index, floor bytes per request and cumulative
floor bytes.

Preregistered, directional only: if persistent human direction matters here, D should reduce
prompt-requirement failures or premature completion after activation. If outcomes match while D
adds bytes, there is no evidence on this ruler that an always-present floor earns its cost — and
that would not generalise to arbitrarily long tasks.

Design digest `bc5d4e0ce8e3bff00ea90fa6f7a1f49a60e45b84ba541ac0b2178ab1338fea64`. Arm C `205279d9c1db4659…`,
arm D `c1afd9223d4e77fa…`.
