# P6-r4 notification wait, enforced timer, delivered-outbox drain — Stage A
(SIMULATED candidate; no live run)

Narrow successor on the archived P6-r3 base (source/tests copied; r3
originals immutable). Three connected corrections, all exercised through
the exact CLI with injected OS boundaries (tmp streams/claims/DB,
PATH-shimmed wake/systemd scripts, explicit evidence args):

- N: production `DirNotifier` (Linux inotify via ctypes stdlib) attached
  BEFORE the initial drain closes the subscribe/read race; persisted
  event reading is the drain, never a periodic poll (`time.sleep`
  removed from the wait path). Startup-existing events observed exactly
  once; timeout/cancel/fd-cleanup proven; overflow/loss/restart
  reconcile against durable cursors/seen sets. Distinct worker/verifier
  streams exercised through the same CLI.
- T: one stable action→unit mapping declared in the bound plan/manifest
  and used by create/query/cancel/callback; host timers are created
  through the configured runner with the remaining authorized duration
  and the executable candidate callback (never `true`); missing
  allowlist or failed creation is an owned failure that reconciles
  delivered work instead of claiming success; callback authority and
  duplicate/stale/early/cancelled rejection hold after reopen. Runner
  paths (wake/systemd) come from the bound plan allowlist.
- O: pending intents settle only on transport-delivered proof PLUS
  ledger evidence (flight or terminal disposition for the target);
  terminal phase alone never forges acknowledgement; queued/ambiguous
  stay pending and keep rollback BLOCKED; crash before/after delivery
  and before/after ack reconcile the same identity with no blind resend
  and no premature clear.
- `fixture-plan.json` setup/run/assertions/cleanup are executable with
  no placeholders — PROPOSED ONLY, never executed here. Retirement
  matrix keeps openwork live; rollback ordered.
- `src/fake.py` is INTERNAL test-only (never a write path, never live).

Run: `PYTHONPATH=src python3 -m pytest tests/ -q` (165 tests: 156
retained + 9 N/T/O gates, injected effects only). Accepted core suite:
59 passed. Simulated evidence never certifies live behavior; Stage C
needs candidate PASS + Tern-signed plan hash first.
