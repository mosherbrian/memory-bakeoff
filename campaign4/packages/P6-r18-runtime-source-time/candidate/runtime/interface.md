# P6-r18 runtime source-time interface (exact, versioned once)

## Who records what
- The **trusted host runtime** records source time at the actual end
  append. Model seats never type a clock and never guess their item.
- Worker/verifier seats emit bound claim/artifact/check content through
  the existing authenticated delivery mapping (unchanged).
- Detection time (observer receipt) is never relabelled source time.

## Source-record format (v1, same-record versioned fields, one append)
`runtime/acp-worker` `emit("end")` delegates to the shipped stdlib hook
`runtime/srcemit.py`, appending exactly one line per turn end:

    {"t": "end", "item": "<runtime item>",
     "src_v": 1, "src_at": "2026-09-23T01:00:05Z",
     "src_session": "<runtime session id>",
     "src_provenance": "runtime-end-append",
     "src_uncertainty_s": 1, "src_clock": "ok|discontinuous|test",
     "src_status": "ok"}

- `src_at`: host UTC at the actual append (`time.time()`), second
  resolution (`src_uncertainty_s: 1`).
- `src_clock: test` marks the fixture-only injected clock
  (`ACP_SOURCE_TEST_NOW` env or explicit `now`); never set on live paths.
- `src_clock: discontinuous` (wall-vs-monotonic divergence past 60 s):
  the stamp is kept but flagged unusable → consumer INCOMPLETE.
- Local copy diff vs pinned `inputs/acp-worker` (`6871ceb1…`) is confined
  to `emit()` + one `_runtime_source_fields` delegate (38 lines).
  The shared `~/.config/agent-deck` runtime is byte-untouched.

## Failure semantics (truthful, never silent, never fatal to work)
- Stamp-helper failure → explicit `src_status: "unavailable"` receipt +
  stderr notice; the turn continues (telemetry never kills model work).
- Append failure → stderr notice + `SourceWriteError`; turn continues;
  downstream sees a missing receipt → INCOMPLETE, never PASS.
- An end proves the turn ended, not work success: stalled/cancelled/
  failed ends without an authenticated valid claim cannot certify
  completed work (existing claim policy unchanged).

## Consumer binding (`source_mode`, declared per manifest)
- `runtime`: join each action's source receipt (from the observed end
  record, persisted to kv at observation) to its own detection via the
  R16 item→action binding. Session/item/execution must match the bound
  current identity; unmatched/stale/duplicate/wrong-execution/conflicting
  source is rejected, never opportunistically matched. Missing or
  `discontinuous`/`test`-unexpected source → explicit INCOMPLETE.
  Sidecar files are ignored in this mode (no silent fallback).
- `sidecar` (default, legacy): the R16 onset-sidecar join, unchanged;
  explicit producer sidecars remain supported with declared provenance.
- Legacy records without reliable source stay explicitly unmeasurable;
  reopen/replay re-reads the same persisted bytes (never a fresh stamp,
  never extended grants).

## Fixture task contracts
Fixture lane tasks (see `fixture-launch-plan.json`) state: the runtime
records source time; worker tasks emit bound claim/artifact/check text;
verifier tasks emit recompute/check text against the worker claim. No
undocumented producer-sidecar task and no synthetic stream emitter exist.
The plan executes the LOCAL instrumented runtime copy only (pinned
hashes); the shared runtime path must never appear in a proposed fixture.
