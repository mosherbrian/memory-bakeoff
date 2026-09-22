# P6-r3 prove the actual recovery CLI — Stage A (SIMULATED; no live run)

Composition repair on the archived r2.1 base (source/tests copied; r2.1
originals immutable): the candidate CLI itself (`src/harness.py`
`setup`/`run-fixture`) now performs dispatch, authorized worker send,
subscribed turn-end wait, route-free claim + recomputed artifacts,
publish, contract-selected verifier send, verifier end, director-
authorized terminal close (or bounded recovery), latency writing and
outbox reconciliation — with injected OS boundaries (tmp stream/claims/
DB, PATH-shimmed wake/systemd scripts, explicit evidence args) running
the SAME parsing/construction/orchestration as live mode.

- Live path uses HostClock (never FakeClock/executor/world); missing
  collaborators fail closed; no fake defaults live. Plan hash is
  verified against the plan file bytes and binds seats/units/wake path;
  non-allowlisted seats refused.
- Sessions/streams bind from explicit launcher evidence (setup refuses
  without them); runtime items bind at observation; durations (never
  absolute example deadlines) derive deadlines from trusted start.
- No-end at bound is owned failure with nonzero exit + latency failure
  sample; latency.jsonl carries real per-action fields with source-vs-
  receipt uncertainty distinguished; gates asserted (zero samples fail).
- Full worker→verifier→director graph through the CLI with receipts and
  ack-after-delivery outbox; fault matrix (no source, slow start,
  missing claim, failed turn, duplicate/stale, truncation, restart)
  yields owned outcomes with no duplicate effects; cleanup verifies
  (unit state, identities, archive-before-delete) before reporting.
- `fixture-plan.json` setup/run/assertions/cleanup are executable with
  no placeholders — PROPOSED ONLY, never executed here. Retirement
  matrix keeps openwork live; rollback ordered.
- `src/fake.py` is INTERNAL test-only (never a write path, never live).

Run: `PYTHONPATH=src python3 -m pytest tests/ -q` (150 tests: 135
retained + 15 black-box CLI acceptance, injected effects only).
Accepted core suite: 59 passed. Simulated evidence never certifies live
behavior; Stage C needs candidate PASS + Tern-signed plan hash first.

## Sole repair (D1 + D2 + D3 + D4)

- D1: setup resolves session/per-seat streams from launcher evidence
  (explicit args or exact evidence command) by creating the
  fixture-owned stream surface, failing closed otherwise; worker and
  verifier ends come from distinct bound streams; wake texts carry the
  plan-pinned task/claim instructions (formatted, never bare ids).
- D2: `harness setup`/`run-fixture` plus `check-latency`/`rollback`
  subcommands run the same production path; host timers are created
  through the configured runner (`create_host` with the candidate
  callback) from the fixture flow; unhandled OwnedFault exits map to
  error JSON + exit 3 (owned code + nonzero preserved).
- D3: `check-latency` requires a positive recovery sample, real
  timestamps on every row, failures retained in denominators, and never
  counts unacked escalation as recovery; latency rows carry source
  timestamps with uncertainty distinguished.
- D4: `rollback` reconciles bound units, current IDs, receipts and
  outstanding intents, archives via the SQLite backup API (WAL-safe),
  and derives its report from those checks — any failure blocks the
  success report; cleanup runs it before deleting state.
