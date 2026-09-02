# pi-observational-memory Gen26 — longitudinal ingestion and lifecycle

## Status

`complete_ingestion_lifecycle_context_unavailable`.

This is a completed three-repetition evaluation of the frozen OM 3.0.4
persistent-RPC ingestion/lifecycle profile. It is not a semantic retrieval
score and it does not contain the planned rendered-context exposure diagnostic.

## Identity and Gen25 correction

The evaluated system was pi-observational-memory 3.0.4 at
`ce9fc982b3a219a7839f07c9f4a3e054e81a2b21`, Pi 0.81.0, one persistent RPC
process per repetition, `qwen3.6-35b-vulkan-nothink` with thinking off at the
frozen LAN endpoint, and Gen24's synthetic OM settings. The Gen26-only harness
component is the per-observation native quiescence barrier.

Gen25's calibration result is preserved: it demonstrated that persistent RPC
avoids the Gen24 stale captured-context failure. Its safe summary is corrected
here only as metadata: public v1 observations were exposed in Gen25's discarded
partial attempt, but no valid v1 result was published.

## Barrier

Before every new observation, the controller snapshots the live-session debug
history and ledger. After Pi emits `agent_settled`, it detects a *new* native
run by `runId` from any observer, reflector, or dropper stage start. A launched
run must reach its own terminal event, then retain a stable same-process ledger
leaf across a one-second race guard. A no-stage-due turn instead requires a
predeclared two-second launch-detection guard and stable same-process ledger.

Focused tests cover no-stage-due, observer and reflector-only runs, stale prior
terminals, terminal errors, ledger races, and session changes. An unrelated live
mini-sequence exercised both observer and reflector-only paths before v1.

## Completed repetitions

All three fresh sessions ingested the 16 publication-safe observations in
canonical order. Every observation passed the barrier and all nine frozen
checkpoints were captured after quiescence. There was no session replacement or
stale-context error.

The product created native observations and reflections. Near the final
checkpoints it also produced native drop tombstones. These are preserved as
lifecycle evidence only: active observation-pool membership is not factual
current truth, and a drop is not automatically deletion, correction, or
supersession.

## Context and retrieval boundary

Pi's supported RPC `compact` operation was tried at checkpoints 8 and 16 of
every repetition. Each time it cleanly declined with `Nothing to compact
(session too small)`. Therefore the native compaction hook did not render an
agent-visible memory context. The required 20-case context-exposure diagnostic
cannot be produced for this frozen short-session profile.

OM's exact-ID `recall` remains provenance recovery, not natural-language
semantic retrieval. No query was sent to an accumulating session, no query
adapter was manufactured, and no Hit@k, reader, or generic scalar score is
published.

The ignored raw traces contain command/event order, PID/session identity,
ledger leaves, debug run IDs, terminal events, and native compaction responses.
The checked-in summary is deliberately sanitized.

## Frozen ruler and verification

The canonical v1 fixture and scorer hashes were checked before execution and
afterward: `a5c67e7b2677dff5c90c91fe0fbc72f251f7e82b97d125122e8ce4ae5eb413dd`
and `1dd831e80b3769af01db01b3acf642ed5f7e0dc2ca1ccf4c37d6c03773759c34`.
The full suite passed: 80 tests, with one pre-existing metadata deprecation
warning.
