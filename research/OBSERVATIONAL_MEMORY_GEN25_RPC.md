# pi-observational-memory Gen25 — persistent Pi RPC

## Status

`calibration_passed; longitudinal-v1_result_not_published`.

This is a narrow driver-method ablation of Gen24. It establishes that the
frozen product can complete its unrelated garden-journal calibration when one
Pi 0.81.0 RPC process remains alive through prompts, inspection, and native OM
background work. It does not publish a longitudinal retrieval, lifecycle, or
reader result.

## Frozen identity

- pi-observational-memory 3.0.4 at `ce9fc982b3a219a7839f07c9f4a3e054e81a2b21`
- Pi 0.81.0
- persistent `pi --mode rpc` JSONL driver, one fresh process per repetition
- `qwen3.6-35b-vulkan-nothink`, thinking off, via
  `http://strix-halo.local:8080/v1`
- Gen24 synthetic settings unchanged: observer 256, reflector 512, chunk 1024,
  pool max/target 1024/512, four worker turns, native dropper, debug enabled.

## Gen24 comparison and local Pi protocol preflight

Gen24's committed calibration invocation was a one-shot/print-mode Pi driver
with a session directory and the OM extension; it reached `observer.records`
then reported the extension's stale captured-context error. The committed
evidence does not establish an intentional harness session reload, so no
stronger historical claim is made.

The installed Pi 0.81.0 package, inspected locally, supports `--mode rpc`.
It launches a strict LF-delimited JSONL stdin/stdout protocol. `prompt`,
`get_state`, and `get_entries` are supported commands; `get_state` returns a
session ID and streaming/compacting state, while `get_entries` returns entries
and a `leafId`. Its RPC event stream includes `agent_settled`.

`src/memory_bakeoff/pi_rpc.py` records every command, response/event, stderr,
PID, state snapshot, and process transition. It never starts a second Pi
process to inspect a live session.

## Frozen quiescence rule

Pi `agent_settled` alone is insufficient because OM launches its observer as a
background task. A repetition is considered quiescent only after all of the
following:

1. the same RPC process reports `isStreaming=false`, `isCompacting=false`, and
   one stable session ID;
2. the relevant `agent_settled` event was received;
3. native OM debug evidence reaches a terminal chain for the triggered run
   (or records a terminal error); and
4. two same-process `get_entries` reads, separated by a one-second race guard,
   retain the same leaf with no new entries.

The one-second window is not treated as completion evidence; it follows the
native terminal stage.

## Calibration result

All three fresh processes completed three unrelated garden-journal prompts.
Each observer recorded observations, the reflector completed with no accepted
reflection, and the dropper cleanly logged `waiting_for_reflection`. The RPC
session ID remained stable throughout normal prompts and inspection. No stale
context error, extension error, reload, or session replacement appeared.

The raw ignored control-plane traces retain the full ordering and native debug
logs. The benchmark-safe summary is
`results/observational_memory_gen25_rpc_calibration/summary.json`.

This supports a limited causal conclusion: Gen24's blocker is
driver/lifecycle-sensitive, and the frozen OM profile is viable under this
persistent-RPC calibration profile. It does not establish that all interactive
drivers or OM versions are safe, nor does it evaluate PR #58.

## Longitudinal boundary

The canonical frozen v1 hashes were reverified through the ruler API:
`a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd` for
the fixture and
`1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34` for
the scorer contract. These are canonical semantic hashes, not the byte hash of
the formatted fixture JSON file.

One authorized public-observation v1 process was started after that check, but
the controller had not yet imposed quiescence between individual observations.
Its observer therefore began a subsequent multi-turn batch before checkpoint
capture; the process ended without a finalized trace. That partial exposure is
not a valid longitudinal repetition and is not represented in the checked-in
result artifact. No query was sent, no natural-language retrieval score exists,
and no lifecycle or reader score is published.

A future authorized continuation must use a fresh profile/repetition and make
the per-observation or per-checkpoint native-pipeline completion boundary
explicit before reporting any v1 result.

## Verification

`pytest -q` passed: 76 tests, with one pre-existing metadata deprecation
warning.
