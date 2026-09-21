# P5-clock-ingress — independent verification

- **Verifier:** corvid (independent; did not author these outputs)
- **Date:** 2026-09-21; one 20-minute pass (P5 verifier grant 40m)
- **Authority:** contract `ca8a9e05…` @ `ec332546`; admission-review
  `8bbb360c…`; P4-r2 accepted at `4c07bd83`; accepted P3-r3 core `d27d5be`.

## Verdict

**PASS.** The trusted ingress owns receipt time and deadline derivation,
caller overrides and forged receipt fields are rejected, occurrence claims are
validated separately with a finite justified tolerance, clock discontinuity is
detected and quarantined with deadlines unchanged, restart preserves
historical receipts and opens a new epoch, the copied lifecycle/store APIs are
the only write path, no method bodies are duplicated, and all 54 local + 59
core tests pass with no live effects.

## Commands and results

```bash
cd campaign4/packages/P5-clock-ingress
PYTHONPATH=src python3 -m pytest tests/ -q        # 54 passed
cd ../P3-r3-authoritative-claims && python3 -m pytest tests/ -q   # 59 passed
```
Plus the independent ingress matrix below in fresh `/tmp` stores with injected
clocks.

## Per-file hashes (recomputed)

| Artifact | sha256 |
|---|---|
| `src/ingress.py` | `f1b39a66112788a96fa41d314163da4da700fdbfd1d16e5eca61092806ba3046` |
| `src/driver.py` | `3fbb58ce6b941b80b74a38abd3844c460bc3b07ff86024067dfd4ce8ea3b1313` |
| `src/store.py` / `lifecycle.py` / `validator.py` | unchanged pinned copies (`dafaeb33…` / `7ebaf466…` / `dcecfc1d…`) |
| `tests/test_ingress.py` | `f0d15f17ef66bec342608a21a3dd45f3959e4de914137a505e0b94a5423352bc` |
| `fixtures/clock-cases.json` | `dacf9dc73651e9826bec842429913f617ca684c5442e1042759ff1bb9259d2fa` |
| `interface.md` / `README.md` / `implementation-report.md` | `df2a7b42…` / `96e71226…` / `f1027f17…` (match supplied) |

## Expected/observed matrix (my unshared cases)

| Case | Expected | Observed |
|---|---|---|
| caller supplies `recorded_at` / `receipt` / `_trusted` | forged receipt rejected | `E_FORGED_RECEIPT` (owner tern) |
| caller legacy `at` | overwritten by trusted time, caller value preserved | `at=2026-09-21T12:00:00Z`, `caller_at_ignored=1999-01-01T00:00:00Z` |
| `occurred_at` naive / minute-only | quarantine | `E_BAD_OCCURRED` |
| `occurred_at` +900 s future | quarantine (>120 s tolerance) | `E_SKEW_EXCEEDED` |
| `occurred_at` +60 s future | accepted | admitted; `skew_s=60.0` |
| `occurred_at` backdated (and with provenance) | retained, both times, no retro-authorization | admitted; `occurred_at=11:00Z`, `recorded_at=12:00Z`, `skew_s=-3600`, provenance kept |
| start event with caller `deadline` | rejected | `E_DEADLINE_FORGE` (owner tern) |
| start duration `0` / `"60"` (non-int) | rejected | `E_BAD_DURATION` |
| start duration over allocation cap | rejected | `E_ALLOC_EXCEEDED` |
| start default duration | derived from trusted start | `deadline=2026-09-21T13:00:00Z`, `duration_s=3600` |
| pinned grant unknown / expired / phase mismatch | rejected | `E_GRANT_UNKNOWN` / `E_GRANT_EXPIRED` / `E_GRANT_MISMATCH` |
| pinned valid far-future grant | accepted, not treated as skew | `deadline=2026-09-21T14:00:00Z`, `grant_ref=g-ok` |
| ledger-invalid event (publish in DRAFT) | ingress passes, ledger still rejects | `E_BAD_TRANSITION` from store |
| wall-vs-monotonic jump > 60 s | quarantine, deadlines unchanged | `E_DISCONTINUITY`, evidence owner `cairn`, "deadlines unchanged"; `reconcile_clock` opens a new epoch and the next append succeeds |
| restart / reopen | historical receipts replay unchanged; new epoch | `c1.at == receipt.recorded_at == 12:00:00Z`; new epoch ≠ recorded epoch |

## Structural checks

- **Single accepted write route:** only `src/ingress.py` calls
  `store.append` / `store.record_terminal`; `driver.py`, `status.py`,
  `supervisor.py` contain no direct store writes (driver routes every event
  through `self.ingress`).
- **No duplicated method bodies:** AST scan of every class finds no duplicate
  method names except the legitimate `now` property getter/setter pair in
  `FakeClock`; `driver.py` is 611 lines with unique methods.
- **No live effects:** `src/` contains no subprocess/socket/signal/os.kill/
  os.system/popen/requests/urllib/time.sleep/while True; host time is read only
  by `HostClock`, injected fakes in tests; no host clock change, no
  `state.json`, no live adoption.
- **Tolerances** are finite and justified (`FUTURE_SKEW_TOLERANCE_S=120`,
  `DISCONTINUITY_THRESHOLD_S=60`), applied only to source-occurrence vs trusted
  receipt, never to deadlines; a far-future granted deadline is valid.
- **Backward compatibility:** 54 local (36 rehearsal/durable + 18 ingress) and
  59 accepted core tests pass; lifecycle/store/validator are the pinned copies.

## Limitations

- Simulated evidence only; host UTC proves receipt time, not occurrence, and
  cannot certify live adoption or protect against out-of-band SQLite rewrites.
- The 54-test suite is worker-authored; my matrix above is the independent
  basis for the behavioural claims, alongside the passing regressions.
- No repair/disposition requested; this is a PASS verdict for Tern's boundary
  decision. No live effects or host clock change were performed.
