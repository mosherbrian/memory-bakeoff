# P4-integration-rehearsal — post-repair verification (P4-verify-2)

- **Verifier:** corvid (independent; did not author these outputs)
- **Receipt:** `postrepair-verification-receipt.json` — action `P4-verify-2`,
  start `2026-09-21T22:01:46Z`, deadline `2026-09-21T22:21:46Z`, allocation
  1200 s
- **Baseline:** contract `c0f31dd0…` @ `53c901bb`; accepted P3-r3 core
  `d27d5be…`
- **Preserved:** `verification.md` is untouched; this file is the post-repair
  verdict for the repaired tree.

## Verdict

**PASS** for the present repaired tree. The version block is resolved by the
recorded, allocated sole repair; the removed/never-armed timer no-op is fixed,
a genuine due deadline remains one-shot, all 16 rehearsal and 59 core tests
pass, no live effect is possible, and the present manifest matches the receipt
exactly. Readiness for a live fixture remains **NOT ready** (simulated evidence
only; no live adapter reviewed).

## Present manifest (recomputed; 14/14 match receipt)

All 14 receipt paths recompute byte-exact (0 mismatches), including:

| Artifact | sha256 |
|---|---|
| `src/driver.py` | `4726a583dc0a3405a271a656d61f3ebc59d1cfbde84a78f24e5ff101d55413c6` |
| `tests/test_rehearsal.py` | `3838b03a9ab066a9b12a8b2173cd0dd6685f7d62d3610518d9e6acd2b4936522` |
| `src/store.py` | `dafaeb333acc255a5c59de782e6f8be4c71a77322ac59247d232138639178242` (import-line drift, untouched) |
| `src/lifecycle.py` / `src/validator.py` / `src/fake.py` | byte-identical to accepted `d27d5be` |

## Version reconciliation (independently checked)

- `campaign4/p4-attempt-history/initial-recovered/` contains the 14 pre-repair
  files; I recomputed all 14 against `recovery-provenance.json` — **0
  mismatches**. The archive is an after-the-fact reconstruction (documented as
  such), not a claimed timely preservation.
- Recorded history: initial completion `2026-09-21T21:03:19Z` (reported
  `driver.py 181f5b99…`, `tests ae8179b5…`); corvid FAIL `2f0bbfb6…`; authorized
  sole repair dispatched `21:58:41Z`; repair completed `21:59:19Z`
  (`driver.py 4726a583…`, `tests 3838b03a…`). `version-reconciliation.json`
  records `initial_timely: true`, `repair_timely: true`, and that the
  controller TSV September-22 dates are erroneous against September-21
  host/session timestamps.

## Reproducers (archived initial vs repaired present)

| Case | Archived initial (pre-repair) | Present repaired |
|---|---|---|
| removed deadline | `stops=1 wakes=1` (`interrupted`) — the original FAIL | `stops=0 wakes=0` (`no-op-not-armed`) |
| never-armed deadline | (not handled) | `stops=0 wakes=0` (`no-op-not-armed`) |
| genuine due deadline | `stops=1 wakes=1` | `stops=1 wakes=1`, second call `already-handled` (one-shot preserved) |

## Regressions and safety

- `PYTHONPATH=src python3 -m pytest tests/ -q` → **16 passed** (14 + removed-deadline
  no-op + never-armed no-op), 0.04 s.
- Pinned P3-r3 core suite → **59 passed**.
- Prior fault matrix unchanged and passing: crash-before-delivery, ambiguous
  delivery, crash-after-ack, repeated completion/deadline/trigger, stale
  snapshot, legitimate rest with no auto-authorize, missing disposition
  (`E_MISSING_DISPOSITION`), blocked verifier resume (same attempt, no worker
  rerun), stale worker timer cannot expire verifier (`ACTIVE`).
- **No live effects:** `src/` contains no subprocess/socket/signal/os.kill/
  os.system/popen/requests/urllib/time.sleep/while True; stdlib only; fake
  adapters/clock only; `notify` refuses Brian.

## Limitations

- Simulated evidence only; fake adapters cannot certify live launch/inspect/
  stop/wake behavior.
- The pre-repair archive is an after-the-fact reconstruction, not timely
  preservation; the reconciliation relies on session-history hashes and the
  recorded repair dispatch/completion.
- No explicit repair deadline receipt/timer evidence was located and none is
  retroactively certified (per `version-reconciliation.json` deviations).
- Timeliness is recorded by the reconciliation (`initial_timely: true`); I did
  not independently reconstruct controller TSV timestamps, and the erroneous
  September-22 rows remain as recorded.

## Readiness

NOT ready for a separately authorized live fixture: no live adapter has been
reviewed or enabled, no real campaign-history validation exists, and director
live authorization is absent. Simulated evidence proves composition boundaries,
not live behavior.
