# P4-r2-durable-events — post-repair verification (P4r2-verify-2)

- **Verifier:** corvid (independent; did not author these outputs)
- **Receipt:** `postrepair-verification-receipt.json` — action `P4r2-verify-2`,
  start `2026-09-21T22:40:08Z`, deadline `2026-09-21T23:00:08Z`, 1200 s
- **Authority:** contract `ad6df34a…` @ `cdd0ee2f`; archived initial
  `p4r2-attempt-history/initial/` (driver `0ed3f3fb…`, 415 lines); repaired
  present driver `b285bc7f…` (944 lines); accepted P3-r3 core `d27d5be`.
- **Preserved:** the initial PASS `verification-r2.md` (`e2e617f5…`) is untouched;
  this is the post-repair verdict.

## Verdict

**FAIL** — one bounded, repair-introduced artifact defect. All required
behavioural checks pass (D1, D2, genuine due, 36 local + 59 core tests, no live
effects), but the repaired `src/driver.py` is malformed by massive duplicated
method blocks that the bound manifest would freeze. Behavioural correctness does
not excuse certifying a corrupted artifact.

## Manifest and suites

- Receipt manifest: all **16/16** paths recompute byte-exact (0 mismatches).
- `PYTHONPATH=src python3 -m pytest tests/ -q` → **36 passed** (28 retained +
  8 repair tests). Pinned P3-r3 core → **59 passed**.
- No live effects: `src/` has no subprocess/socket/signal/os.kill/os.system/
  popen/requests/urllib/time.sleep/while True; stdlib only; independent
  file-backed `FakeExternalWorld`; `notify` refuses Brian.

## D1 — per-effect crash boundaries (archived initial vs repaired)

Independently injected a `RuntimeError` in `ext.wake` after `ext.stop` delivered,
then reopened a fresh `Driver` + fresh adapters sharing the file-backed world:

| Step | Archived initial `0ed3f3fb` | Repaired `b285bc7f` |
|---|---|---|
| first `on_deadline` | raises after stop; stop delivered, no ack | raises after stop; stop delivered, no ack |
| reopened `on_deadline` | `interrupted`, **new stop (duplicate)** | `recovered`, **0 new stops** |
| world stops | `stop:w` | `stop:w` (single delivery) |

Repaired result: a delivered stop is not repeated after reopen; the pending wake
completes/reconciles per effect.

## D2 — explicit cancellation vs lost timer

| Case | Archived initial `0ed3f3fb` | Repaired `b285bc7f` |
|---|---|---|
| `timer.remove(current)` then due callback | `interrupted`, BLOCKED, 1 stop/1 wake | `no-op-cancelled`, RUNNING, 0/0 |
| cancellation across reopen | n/a (no durable cancel) | `no-op-cancelled`; `reconcile_restart` → `cancelled-owned` |
| accidental loss (no cancel record) | reconstructs and enforces | `deadline:w` re-armed from ledger facts; genuine due enforced once |

`test_repair.py::test_d2_cancelled_package_stays_ledger_accountable` confirms
cancellation does not cancel the ledger deadline: supervision still returns
INVALID (owned, no unowned-silence escape).

Stale/early/rotation probes on the repaired tree are no-ops with phase
preserved (`no-op-cancelled` after rotation, `no-op-early` before due); genuine
due worker/verifier/handoff interrupt exactly once.

## The defect (bounded)

`src/driver.py` (`b285bc7f…`, 944 lines) contains byte-identical duplicated
method definitions inside `Driver`, proven by AST extraction (identical source
segments):

- `_maybe_crash` — **19** definitions (lines 233, 257, 281, 305, 329, 353, …)
- `cancel_deadline` — **18** definitions (lines 238, 262, 286, 310, 334, 362, …)
- `is_cancelled` — **18** definitions (lines 254, 278, 302, 326, 350, 378, …)
- plus **7** duplicated identical comment lines
  ("# Authoritative actor mapping: worker prose never supplies identity.",
  lines 166–173).

The archived initial file is 415 lines; the repair added ~529 lines of
duplication. Python keeps only the last definition, so behaviour is currently
unchanged and tests pass, but the artifact is malformed, the receipt manifest
binds the bloated bytes, and this is a repair-scope anomaly, not a designed
state.

**Required correction:** remove the redundant duplicate definitions and comment
lines from `src/driver.py` with explicit rationale, changing no semantics and no
other file; then re-hash and re-verify. No accepted-core semantics are involved
(driver-local only). No worker/verifier grant is requested here; per the dispatch
this returns to Tern for the next boundary decision.

## Limitations

- Simulated evidence only; cannot certify live launch/inspect/stop/wake.
- The initial PASS (`verification-r2.md`) is retained unchanged as the record of
  the pre-repair tree; this verdict concerns the repaired bytes only.
- I did not assess code style beyond the duplication; the defect above is the
  only artifact-integrity defect found.
