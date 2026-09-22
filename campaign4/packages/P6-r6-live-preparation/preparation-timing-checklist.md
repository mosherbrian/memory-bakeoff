# P6-r6-live-preparation — preparation/timing checklist (pinned before worker)

- **Author:** corvid (independent reader; pins observables before worker)
- **Date:** 2026-09-22; bound to contract `f2b7df48…` @ `e32c0dc`
- **Parent:** P6-r5 `dad98827…`, `candidate-review-repair-2.md` `f20527d2…`
  (injected PASS preserved, not live acceptance)
- **Rule:** all checks are **blocking**. Under the candidate grant the worker
  authors tools/plan only; **actual idle preparation and Stage C are separately
  held**. No real seat/service, shared-wrapper edit, Signal, all-seat pause or
  clock change under the candidate grant. `SHADOW-REFERENCE-RULING` `afa126f`
  is pinned and does **not** authorize shadow.

## Preparation checks (P)

### P1 — isolated new runtimes only
- **Positive:** preparation creates/starts exactly two **NEW**, uniquely named
  `p6-fixture-*` sessions in the campaign4 profile — worker on `acp-go`, verifier
  on `acp-go-deepseek` — with isolated working directories and **no task
  dispatch during preparation**.
- **Negative:** the four main seats (`tern`/`corvid`/`kiln`/`cairn`) are never
  repurposed/stopped/restarted; no shared wrapper edit; no adoption of an
  unrelated existing session on a name collision; failure fails closed.

### P2 — authoritative binding for BOTH runtimes
- **Positive:** record the returned real `session_id`, profile, seat role,
  launch command, runtime producer root, stream paths, and actual Unix socket
  identity/incarnation for **worker and verifier**.
- **Negative:** reject regular-file fake sockets, wrong role/profile, stale
  incarnation, mismatched stream/root; identity is never inferred from filename
  or title alone.

### P3 — same binding for transport and observer; no forged facts
- **Positive:** transport and observer use the **same** recorded runtime
  bindings; an idle runtime may have no stream yet, so the producer path is
  established from inspected runtime launch facts (never by touching a
  placeholder).
- **Negative:** a `fixture-injected` launcher source, synthetic identity, or
  changed binding rejects **before task wake**. If the pinned setup cannot
  support this, report the bounded blocker; do not forge facts.

### P4 — explicit plan phases and cleanup ownership
- **Positive:** plan phases are explicit — prepare idle resources → bind/hash
  manifest → Tern signature → bounded real worker/verifier fixture →
  independently checked effects/timing/rollback. Cleanup is limited to owned
  exact IDs/units/paths; receipts/ledger archived before deletion; candidate
  effects stopped before cleanup.
- **Negative:** missing signature, fixture-injected source or changed binding
  rejects before wake; no production campaign ledger writes or script
  retirement.

### P5 — real host permission deliberately separated
- **Positive:** preparation cannot silently dispatch an initial model prompt —
  verify launch behaviour and use a supported idle mode (the inventoried
  `agent-deck launch` allows no `-message`); the ≤10m cairn preparation ceiling
  is released only by Tern's separately signed preparation receipt.
- **Negative:** candidate review may not start real seats/services; a probe that
  tries to substitute shims for the live path is rejected.

## Timing checks (T)

### T1 — independent witness, not candidate timestamps
- **Positive:** define observable controlled failure onset/source and host-clock
  capture, action/execution correlation, provenance and uncertainty; a private
  external witness may observe real runtime notifications or instrument an
  explicitly declared fixture fault (no shared-runtime edits).
- **Negative:** candidate decision timestamps are not the source; notification
  observation is recorded with its bound/uncertainty, not asserted as exact
  producer time.

### T2 — correct interval, INCOMPLETE when unmeasurable
- **Positive:** controlled onset corresponds to the fault being judged; measure
  the existing 30 s/180 s detection and 60 s recovery (90 s/240 s totals)
  appropriately; ordinary model execution time is never detection latency.
- **Negative:** missing independent onset/source evidence stays **INCOMPLETE**,
  never a passing latency sample; a late detection fails its actual bound.

### T3 — enumerated live cases within the held 15m run
- **Positive:** include genuine normal handoff and lost
  completion/failure recovery, queued/ambiguous transport/restart, and quiet
  rest from the inherited matrix; enumerate exact cases and feasibility within
  the ≤15m live run.
- **Negative:** do not silently omit cases or claim all from one positive sample;
  injected cases stay separately labelled; unperformed mandatory live evidence
  is **INCOMPLETE**.

### T4 — one-send/durable outcomes retained
- **Positive:** the positive run retains one worker and one verifier send,
  durable outcomes and no duplicates; the injected candidate (189+59) is reused
  unchanged.
- **Negative:** no production campaign ledger writes; no research runs or real
  Signal/all-seat pause test.

### T5 — dry-run evidence, not prose
- **Positive:** candidate review runs the new tools with injected OS
  boundaries/private `/tmp`, inspects actual read-only runtime schemas, and
  includes a dry run of the exact preparation/signature boundary and cleanup.
- **Negative:** a proposed live plan containing synthetic identity or an
  invented onset is rejected.

## Pin / scope

These observables are fixed before worker dispatch and cannot add scope without
a Tern amendment. Candidate PASS returns to Tern and never automatically starts
preparation or Stage C.
