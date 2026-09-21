# P4-r2-durable-events — independent verification

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-21; one 20-minute pass (cumulative P4 verifier cap 80m)
- **Authority:** contract `ad6df34a…` @ `cdd0ee2f`; parent
  `P4-integration-rehearsal` at `945e338`; accepted P3-r3 core `d27d5be`.
- **Admission binding:** `admission-review.md 126b31c0…`.

## Verdict

**PASS** for this sidecar package's performance evidence. The three admitted
parent probes are corrected, deadline handling is authoritative, effects and
triggers are durable across reopen with fresh adapters, ambiguous delivery is
reconciled without redispatch or an exactly-once claim, all prior rehearsal/core
regressions hold, and no live effect is possible. Readiness for a live fixture
remains **NOT ready** (simulated evidence only; no live adapter reviewed).

## Commands and results

```bash
cd campaign4/packages/P4-r2-durable-events
PYTHONPATH=src python3 -m pytest tests/ -q          # 28 passed in 0.06s
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
```
Plus the independent matrix below in fresh `/tmp` state (fake clock/adapters).

## Per-file hashes (recomputed; authoritative)

| Artifact | sha256 |
|---|---|
| `src/driver.py` | `0ed3f3fb158d06c85d0ae0735b753c6917998bb6c86c70f963b83397ebff5110` |
| `src/store.py` | `dafaeb333acc255a5c59de782e6f8be4c71a77322ac59247d232138639178242` |
| `src/lifecycle.py` | `7ebaf466dd47e760b401fa0b1d8c2c2d8a1fd26549b0b91a0bfdbb47f498c03f` |
| `src/validator.py` | `dcecfc1d95a75c30a9ecca9a80df6418f930e03d4525fc2b5f38ab31997666c5` |
| `src/fake.py` / `supervisor.py` / `status.py` | `fe7d4ef7…` / `a71b10db…` / `c894ae41…` |
| `tests/test_durable_events.py` | `413579b9c5aab011d9f3af68c3c5e09ffdf87434b5ca29c9fe2010f98ac16044` |
| `tests/test_rehearsal.py` | `0b861c2efa76e68edd6b026587706f5c594fba65e42c596686318b1bba3208ca` |
| `fixtures/probes.json` | `e2577b40281e9be0406617a42168411fd2f358efb28bd8d471ba092a7b78a864` |
| `rehearsal-report.md` / `interface.md` / `README.md` | `59068369…` / `387b4a0b…` / `9814d7c0…` |

The supplied src/tests/fixtures **group sums** (`777d2551…`, `58c8bffb…`,
`8dfab617…`) were not reproducible by any sorted-per-file manifest method I
tried; they are non-authoritative per the dispatch. The per-file hashes above and
the behaviour below are the authoritative basis. (`fixtures` contains one file,
whose hash `e2577b40…` matches the supplied probes hash.)

## Expected/observed matrix (fresh /tmp state)

| Case | Expected | Observed |
|---|---|---|
| probe1 stale worker during CHECKING (past worker DL, before verifier DL) | no-op, CHECKING preserved | `no-op-stale-action`, CHECKING, 0 stop/0 wake |
| probe2 early current deadline (now < deadline) | no-op | `no-op-early`, RUNNING, 0/0 |
| probe3 handled deadline redelivered after reopen (fresh Driver + adapters, shared independent world) | no repeat effect | first `interrupted` (1/1); reopened `already-handled`, 0 new stop/wake; world `stop:w` delivered once |
| genuine due verifier after rotation | interrupt once | `interrupted`; second `already-handled`; 1/1 |
| genuine due handoff | duty-owned wake once | worker callback `no-op-handoff-owned`; `on_handoff_deadline` `interrupted`; repeat `already-handled` |
| wrong action / other package | no-op | `no-op-stale-action` / no-op |
| never-armed action | no-op | `no-op-no-current-action` |
| ACTION_DUE trigger dedup across reopen | durable | second call `True` |
| interrupted effect acknowledged in world; reconcile | `effect-already-handled` | as expected |
| crash-ambiguous delivery | hold, no blind replay | `hold-for-reconciliation`, launches unchanged |

The prior parent removed-timer regression is retained in corrected form: after
`publish_completion` the worker timer is rotated/cancelled
(`deadline:a-w1` absent) and the stale worker callback no-ops
(`no-op-stale-action`) with CHECKING preserved; the never-armed case no-ops
(`no-op-no-current-action`). `test_rehearsal.py`'s misleading cases (crash-settle
via in-memory state, restart reconstruction with caller-armed timers) are
corrected to drive the independent world and ledger facts.

## Durability and authority

- Intents and handled/acked effects persist in a `driver_kv` table in the same
  SQLite database (`intent:<action>`, `handled:<effect>`, `trigger-seen:<t>`);
  fresh Drivers and fresh adapters sharing the independent `FakeExternalWorld`
  cannot repeat acknowledged stop/wake/trigger effects across reopen.
- `on_deadline` checks authoritative ledger facts (current flight action,
  phase, deadline) plus current UTC time before acting; `FakeTimer` is
  explicitly non-authoritative. `reconstruct_timers()` re-arms from ledger
  facts only. `reconcile_restart` never blindly redispatches and makes no
  exactly-once claim; no new attempt or budget reset on recovery.

## Safety

- No live effects: `src/` contains no `subprocess`/`socket`/`signal`/`os.kill`/
  `os.system`/`popen`/`requests`/`urllib`/`time.sleep`/`while True`; stdlib only;
  `notify` refuses Brian; external delivery is an independent in-memory/file
  `FakeExternalWorld`.
- 28 rehearsal/durable tests + 59 accepted core tests pass.

## Observations and limitations (non-blocking)

- By design the in-memory timer is non-authoritative: explicitly calling
  `timer.remove()` for the *current* action's deadline and then invoking
  `on_deadline` past that ledger deadline still interrupts. In the driver's own
  flow a removed current-action timer is unreachable — removal happens only as
  rotation when the flight changes (handled as `no-op-stale-action`) — so this
  is a deliberate consequence of ledger authority, not a relaxation. The
  contract's "removed … cannot interrupt current work" is satisfied through
  rotation/stale-action detection.
- Simulated evidence only; it proves composition and durability boundaries, not
  live launch/inspect/stop/wake. Explicit upstream-failure-event integration
  remains a future live requirement. No live adapter is reviewed/enabled and no
  live authorization exists.

## Readiness

NOT ready for a separately authorized live fixture. No blocking defect found in
this package.
