# P6-live-recovery — repair candidate recheck

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-21/22; one ≤20-minute candidate recheck (remaining P6
  verifier grant)
- **Authority:** contract `174377f1…` @ `91f19cf3`; `director-repair-decision.md`;
  rejected initial archived `p6-attempt-history/initial/` (32 files).
- **Preserved:** first review `candidate-review.md` (`f3171653…`) untouched.

## Verdict

**FAIL** — one bounded defect in the newly required runnable host path. D2
(atomic replacement / receipt+cursor), D3 (trusted receipt time, separate
occurrence, conflict rejection) and D4 (durable one-shot timers across restart)
are corrected and independently reproduced, the exact `fixture-plan.json`
commands now invoke the candidate, the observer and trail correlation work, the
driver change is additive only, and 107 local + 59 core tests pass with no live
effect during this check. But `HostWakeTransport.send` — which the fixture plan's
exact command enables and invokes — passes an invalid keyword to
`subprocess.run`, so the "runnable host path" would raise `TypeError` instead of
performing a bounded live send.

## Bound hashes (recomputed)

| Artifact | sha256 |
|---|---|
| `src/host_adapter.py` | `6525eb1b5f22230ea410ad5c409131565b36a36122da80ca2c530954a4230a33` |
| `src/driver.py` | `3e1136bf335815879b1aa27c177a84b1b1579c302144b8a8ceddc7ca720841af` |
| `tests/test_host_recovery.py` | `23dead83c006cc8872da4e7d6189a258ca2653160ac9ad9bd1f6649d9b135673` |
| `tests/test_repair_p6.py` | `499ca921bb298df0da241c1ab7b049900289afdd9e79ddec1a1cdf599508ba4f` |
| `fixture-plan.json` | `9af17a2abdb55a326dc9468a74eba66d682b328cda870cfceced5605f75ebf82` |
| `implementation-report.md` | `932f5630ba1cf64a55d2bd8194493bed257bd73db6bf1a643b698ae9fa58a9bd` |
| `interface.md` / `README.md` | `8863e055…` / `842556fe…` |

## Commands and results

```bash
cd campaign4/packages/P6-live-recovery
PYTHONPATH=src python3 -m pytest tests/ -q        # 107 passed
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
```

## Accepted semantics

`src/driver.py` changed (additive only): `_kv_put_many` commits a declared
multi-key update in one transaction and `_kv_reload` refreshes the in-memory
projection on failure. No existing method or lifecycle/store/validator behaviour
changed; all seven P5 test files are byte-identical; 83 P5 regressions retained
within the 107.

## Expected/observed (independent injections, fakes only)

| Family | Case | Observed |
|---|---|---|
| D1 | `HostWakeTransport` disabled send | `E_DISABLED` (fail-closed) |
| D1 | exact fixture-plan command enables `send` | would raise **`TypeError`** (see defect) |
| D1 | `ACPOutcomeObserver.observe` hit / miss | hit dict / `None`; `reconcile_observed` miss → `E_UNAVAILABLE` |
| D2 | `replace_action` then reopen | A=`SUPERSEDED->B`, B=`ex2` — coherent after reopen |
| D2 | forced mid-transaction failure in `_kv_put_many` | `ProgrammingError`; first key **not** in projection (reloaded, no partial) |
| D3 | `capture` caller `2099` occurrence | `E_SKEW_EXCEEDED` |
| D3 | trusted receipt stamp | `receipt_at_utc=12:00:00Z` (from injected trusted clock), `occurred_at=11:59:00Z` separate |
| D3 | conflicting re-capture / identical re-capture | `E_CONFLICT` / idempotent `(key, True)` |
| D4 | fire twice same process | `fired` then `already-handled` |
| D4 | fresh `FakeTimerService` over same kv | `already-handled` (durable across process) |
| D4 | cancelled then fire | `no-op-not-armed` |

`fixture-plan.json` now names exact executable commands (host wake send, host
timer command, read-only ACP observer, cleanup) and binds fixture IDs/seats.

## The defect (bounded)

`src/host_adapter.py:105` in `HostWakeTransport.send`:

```python
proc = subprocess.run(cmd, capture_output=True, timeout_s=None,
                      timeout=self.timeout_s)
```

`subprocess.run` has no `timeout_s` parameter (verified:
`'timeout_s' in inspect.signature(subprocess.run).parameters` → `False`), so
when the transport is enabled — exactly as `fixture-plan.json`'s first exact
command does (`HostWakeTransport(..., ('p6-fixture-worker',), True).send(...)`)
— it raises `TypeError: __init__() got an unexpected keyword argument
'timeout_s'`. The handler catches only `(OSError, subprocess.SubprocessError)`,
so this is an uncaught crash, not a bounded send receipt. The Stage-A disabled
path and the D1 test (`test_d1_exact_commands_bind_fixture_plan`) only inspect
`command_for`/plan strings, so the enabled path is unexercised and the defect
was not caught.

**Required correction:** drop the invalid `timeout_s=None` (keep the valid
`timeout=self.timeout_s`, or inject the runner/kwargs so tests can exercise the
enabled path without a live effect), then re-hash and re-verify. No accepted-core
semantic change is involved (host adapter only).

## Limitations

- Stage C remains held: no live effect, no service installation, no seat action,
  no host clock change occurred during this check; I did not execute the wake
  script, the timer command or any host process.
- Simulated/fake evidence only; the defect above is a static/runnable-path
  finding, not a live-run result.
