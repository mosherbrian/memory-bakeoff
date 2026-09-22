# P6-r5-launch-binding — launch acceptance checklist (L1–L4)

- **Author:** corvid (independent reader; pins observables before worker)
- **Date:** 2026-09-22; bound to contract `40fce2e2…` @ `e40ce397`
- **Parent reproduced:** `P6-r4` @ `efc3f827` — exact CLI probe gives
  `terminal-rest` rc0 with **2** verifier sends for one action (L1 real).
- **Rule:** all four are **BLOCKING**. Grading is on the exact shipped CLI with
  injected OS boundaries and private `/tmp` notification only. Total sends,
  dispatch-only producer knowledge, real stream binding and timestamp-free
  events are checked against observables, not helpers.

## L1 — one durable sender
- **Positive:** exact CLI trace has exactly **one** `wake` call to the worker
  seat and **one** to the verifier seat for the authorized actions; the single
  outbox message carries the complete task/pinned-brief pointer. The run reaches
  `terminal-rest`/`transition-committed` with one verifier dispatch.
- **Negative:** no second harness send alongside the outbox; a repeated
  dispatch/restart does **not** create a fresh message identity; ambiguous ack
  is not blindly resent; reopen/crash before/after ack reconciles the same
  identity; O receipt+execution evidence and atomic settle retained (terminal
  alone is no proof).
- **Parent failure:** 2 verifier sends (`{"kind":"verifier-dispatch"…}` then
  `TASK-V run p6h-v1`). FAILS.

## L2 — actual launcher binding
- **Positive:** an executable, allowlisted preparation step (not a `cat` of a
  file nobody creates) resolves the actual session, per-seat runtime stream
  key/path and producer root from read-only discovery; setup fails closed
  **before wake** when binding is missing; distinct runtime incarnations bind
  explicitly; stale/foreign ends are not adopted merely because first observed.
- **Negative:** no `-worker`/`-verifier` key inference, no fabricated runtime
  stream, no truncation of an existing producer file; if an isolated
  `ACP_STATE_HOME`/bridge is used, launch, producer, transport socket and
  observer consistency + cleanup are specified and no shared wrapper is edited.
- **Parent failure:** plan reads nonexistent
  `/tmp/p6h/launcher-evidence.json`; setup creates empty derived
  `stream-key-worker/verifier` files. FAILS.

## L3 — dispatch-sufficient claims
- **Positive:** the worker message carries the concrete trivial artifact task,
  exact launch-assigned execution/attempt/step, atomic claim path/schema,
  permitted artifact root and relevant pinned input; the verifier message
  carries the artifact/claim binding, an independent deterministic check and its
  own claim identity. A **fresh producer** sees only the actual outgoing message
  and the files it names — it does not read hidden test manifest variables or
  pre-stage claims/end events. Positive and negative verdicts are required; a
  completed verifier turn reporting a failed check cannot close COMPLETE.
- **Negative:** neither worker chooses routing nor supplies director authority;
  the routing-free claim contract is preserved; missing claim → bounded owned
  recovery, never invented success.
- **Parent failure:** task texts give only action + claims dir (no
  execution/step/schema/artifact/check); tests fabricate claims from undispatched
  manifest vars. FAILS.

## L4 — honest timing on real-format events
- **Positive:** demonstrate actual-format `emit(end)` events (no `at` timestamp)
  flowing through the production observer; host-stamped observation and
  independent fault-injection onset/source evidence are each recorded with
  provenance and uncertainty; explicitly state which acceptance intervals are
  establishable (30 s/180 s detection, 60 s recovery, totals 90 s/240 s).
- **Negative:** missing source time remains **unmeasurable, never zero**; no
  timestamp added only to test records; observer time is never substituted for
  source time; any private producer instrumentation/bridge is in the exact plan
  and labelled; no shared runtime edits.
- **Parent failure:** latency `source_at` requires `end.extra.at`, but the
  inventoried `acp-worker` emits end without a timestamp. FAILS.

## Retention / scope

All N/T/O and 172+59 semantics are retained; tests must not preserve a known
bug; accepted-core changes require director review first. No broad rewrite; no
live seats/services, Signal, main-seat reset, wrapper edit, clock change or
retirement in candidate work. The checklist cannot add scope without Tern
amendment.
