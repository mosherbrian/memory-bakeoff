# The first paired Pi coding pilot: design, frozen

**Evidence class:** `architecture_pilot_design_no_score`. Nothing here was run against a model. No
inference, no GPU, no hosted API, no network during the preflight — the last of those is proved
by blocking the socket layer and attempting a connection, not asserted.

Gen43 showed the architecture is mechanically implementable on Pi. Gen44 turns it into an
experiment that can be run once and read honestly: arms, composition, tasks, measurements, order
and model identity are all frozen and digested **before** any live run exists.

## The model candidate, pinned without generating a token

| field | value |
| --- | --- |
| served alias | `qwen3.6-35b-vulkan-nothink` |
| model | Qwen3.6-35B-A3B, UD-Q4_K_XL (general.file_type 15, quantization_version 2) |
| model file | 22,360,456,160 bytes, sha256 `707a55a8a4397ecde44de0c4…` |
| architecture | qwen35moe, GGUF v3, 733 tensors |
| chat template | embedded, applied via `--jinja`, sha256 `55d4931433fe502b794226ee…` |
| server | version: 385 (2041049), Vulkan |
| device | Vulkan0: AMD Radeon 8060S Graphics (RADV GFX1151), 127488 MiB total |
| context | 131,072 tokens, reasoning `off` |
| sampling | temp 0.6, top_p 0.8, top_k 20, min_p 0.0 |
| router | llama-swap on 0.0.0.0:8080, TTL 3600s |

Status **PINNED**. Everything above comes from the on-disk config, the GGUF header,
the binary's own `--version` and `--list-devices`, and the running unit. The server was never
started for this generation.

### Risks Brian should see before authorising Gen45

1. No seed is pinned and temperature is 0.6, so individual runs are stochastic. Either the request path must carry a per-request seed, or repetitions must be treated as samples rather than reproductions. This is the single largest threat to the paired design and needs deciding before the first live run.
2. --reasoning off is a server-side flag, not a model property. Whether Pi's provider path re-enables a thinking channel has not been verified without generating.
3. Tool-call formatting under this chat template has not been exercised with Pi; template compatibility with Pi's tool protocol is unverified and is a real blocker risk.
4. llama-swap's 3600s TTL means prompt KV cache can persist across runs. Arm B sends a different, shorter prefix than arm A, so cache warmth differs by arm by construction; wall-clock and prefill numbers must not be read as an architecture effect.
5. The 131072 context window is far larger than any arm is expected to reach, so arm A is unlikely to hit native truncation on four small tasks; Pi's own compaction threshold, not the model window, is what arm A will meet first.

The first one is the one I would not proceed past quietly. A paired design with three
repetitions per cell assumes the repetitions mean something; at temperature 0.6 with no pinned
seed they are samples, not reproductions. That is survivable — it just has to be *decided*, and
said out loud in the report, rather than discovered afterwards.

## Arms

**A `pi_default_v1`** — stock Pi context and history, its own compaction enabled, ordinary coding
tools, no extension touching the request.

**B `pi_state_control_v1`** — the Gen43 lineage: composed context replaces transcript replay,
history is externalized losslessly, Pi's compaction is cancelled, control gates completion on a
validated artifact, and three tools exist to drive state and control.

The treatment is that whole bundle:

- composed context replaces transcript replay
- executable phase transitions with a gated completion
- bounded validated structured state
- artifact receipts outrank state
- three extra tools that exist only to drive the above

Arm B is not "arm A with fewer bytes", and this report will not pretend otherwise. Four tasks
cannot attribute a difference to any single component of that bundle.

There is no arm C. On-demand historical retrieval is a later ablation; first find out whether B
is sufficient without it.

## What B sends, frozen now

Composition order: `immutable_instructions`, `control`, `state`, `recent_window`, `latest_observation`, `artifact_refs`.

Caps: state 4,096 bytes (inherited from Gen43), recent
window 2 complete interaction units under
8,192 bytes, latest observation
8,192 bytes. Overflow stays in history with a
stable reference; nothing is deleted.

The unit rule is mechanical rather than a matter of judgement, because Gen43's one-message
composition was too brittle to assume for a real model:

> a unit starts at a user message and runs to the message before the next user message; a trailing partial unit counts as one unit; messages before the first user message belong to no unit and are never included

That rule is tested against fixtures, including the orphan case of messages that precede the
first user turn.

## Both arms verified inside the installed Pi

Handed a synthetic transcript of 36 messages and
33,535 bytes:

| check | result |
| --- | --- |
| a does not replace context | True |
| a keeps pi compaction | True |
| a leaves pi array untouched | True |
| b cancels compaction | True |
| b replaces context | True |
| b window is bounded | True |
| both capture request sizes | True |

Arm A passed 33,535 bytes through untouched and returned no
replacement, so the baseline is genuinely stock Pi with instrumentation beside it rather than in
front of it. Arm B returned 7 messages of
5,991 bytes. Pi 0.73.0, core patched
false.

## Tasks

Four invented fixture repositories, unrelated to every corpus here and to the Gen43 trace.

| task | shape | files | frozen tree | fails before | passes after reference fix |
| --- | --- | --- | --- | --- | --- |
| T1 | cross-file bug fix with a decoy | 6 | `c5f74d27399a` | True | True |
| T2 | coordinated API change preserving behaviour | 6 | `671fb3bb2475` | True | True |
| T3 | debugging under noisy tool output | 4 | `ad03f75d8c8a` | True | True |
| T4 | regression that reopens an earlier decision | 4 | `6ae275d23e74` | True | True |

What each one puts pressure on:

- **T1** — the decoy module contains a similar-looking but correct conversion
- **T2** — three files must change together and old callers must keep working
- **T3** — the failing signal is buried in ~200 lines of irrelevant console output
- **T4** — the obvious one-line fix satisfies the visible test but breaks the midpoint rule stated in the module's own design note

Each task was proved solvable here, without a model, by applying a reference fix that lives only
in the builder script. It is never written into a fixture tree, never appears in a prompt, and is
not committed anywhere the agent can reach. The hidden verifier sits beside the repository, not
inside it — the preflight checks that the agent cannot see the verifier
(True) and that neither the repository nor the
prompt names it (True).

## Measurements, frozen

Primary: deterministic verifier pass or fail on the final repository state.

Co-primary: provider request bytes at every model call, cumulative request bytes across the run, max and median request bytes, request bytes by turn index, model calls, tool calls.

Churn is defined before it is counted, because a definition settled after the fact can be bent:

- **exact repeated tool call** — same tool name and canonicalized JSON arguments as any earlier call in the same run
- **redundant file read** — same path and byte/line range read again with no intervening write to that path in the run's own tool log
- **redundant verifier invocation** — same canonical verifier or test command repeated with no intervening repository mutation, judged by the worktree digest

The definitions deliberately overlap. A verifier re-run after an edit is an exact repeat but not
a redundant invocation, and both counts are reported rather than merged. The counters were
checked against a hand-written log whose expected numbers were written down first
(True for the match).

Termination is classified separately from task success, because artifact-gated completion will
produce runs that stop short rather than declare victory:

- **abandoned or timeout** — the run ended without verifier success
- **correctly blocked** — arm B refused an unearned completion; a control success, not a task success
- **orchestration failure** — the harness or extension failed; not a model result
- **unearned completion attempt** — the model tried to finish while the verifier or receipt was invalid
- **valid completion** — verifier passes and, in arm B, the gate also validates

## Run plan

24 runs: 4 tasks x
3 repetitions x 2 arms, serial, fresh worktree and fresh Pi
session each time. Order is deterministic from seed 20260905, arms paired on task and
repetition, adjacent within a pair, with the first position counterbalanced
(True) so arm order cannot align with machine drift
or cache warmth.

## Reading rules, agreed in advance

- four tasks and three repetitions is descriptive paired evidence, not a population estimate
- no global winner claim
- every run-level leaf is reported, including crashes and blocked runs
- wall clock stays outside the scientific digest

Hypotheses are directional only: H1: B materially reduces cumulative request bytes on longer or noisier runs; H2: B reduces the growth of request size with run length; H3: B does not reduce verifier success so far that the architecture is unusable; H4: exploratory: B may reduce repeated or redundant tool calls, or increase them; H5: the artifact gate prevents any naturally occurring unearned completion from counting; H6: a failure caused by missing older context is a result, not a reason to retune.

## Preflight

Passed: **True**. Composition caps respected, arm A carries no extra tools, all four
tasks isolated and solvable, worktree reset returns to the frozen tree, order deterministic and
counterbalanced, Gen43's state/control guarantees still hold under the pilot caps — completion
earned from a receipt, state surviving restart, artifact mutation invalidating completion — churn
counters matching the hand-checked log, both Pi arms verified, and outbound network blocked.

## What Gen45 needs from Brian

1. Authorization to run 24 live coding-agent runs against the local Strix Halo server.
2. A decision on the seed question above: pin a per-request seed if the path allows it, or accept
   repetitions as samples and say so in the result.
3. Acceptance that tool-call formatting under this chat template is unverified until the first
   live run, and that a format incompatibility is a plausible early blocker rather than a result.

One operational note: Pi and the inference server are both on the Linux workstation, while this
repository lives on the Mac. Gen45 has to run on Linux, so the fixtures and harness need to be
present there before the first run.

Contract `src/memory_bakeoff/pi_state_control/pilot.py`, sha256 `a44c6b77dc51910a88b0ec1d90b33ac18b52676e76e3a21c439bd6a8819b7d71`.
Design digest `e3ad63bebb3e3252433ed71e30cf6edacb40d5fd2467c462ffb4ab6c8b173973`, rebuilt with wall-clock and machine-local paths excluded.
