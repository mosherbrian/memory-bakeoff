# Kiln R&D pulse — flake sweep, full coverage (2026-09-12)

Completes `KILN-FLAKE-SWEEP-20260912.md` (ring 1) and
`KILN-FLAKE-SWEEP-RING2-20260912.md` (ring 2): with the sentinel repaired
(`3f845c9`) the whole suite now runs in-lane in ~55 s, so the sweep's final
form is affordable — the ENTIRE suite, not a ring subset. Guard meta-suite
excluded per `tests/RUN-AS-COMMITTED.md`. $0, no live-window contact.

## Result: 4 full-suite runs, zero variance

| Run | Outcome | Wall |
|---|---|---|
| full-run 1 | 26 failed, 1600 passed, 3 skipped, 5 errors | 55.2 s |
| full-run 2 | identical | 53.7 s |
| full-run 3 | identical | 54.6 s |
| `PYTHONHASHSEED=7` | identical | 52.8 s |

Every failing/errored id is a KNOWN_FAILURES.json entry — 26 + 5 = 31,
exactly the baseline count, and the sentinel independently verified the
IDENTITY of the set this morning (zero unlisted, zero stale). The suite's
red is precisely the recorded red, and none of it is flaky: same ids,
same counts, every run, both hash seeds.

## Sweep final state

- **Coverage:** complete (1,634 collected incl. 3 skips; guard meta-suite
  excluded by design).
- **Flakes found: 0** across ring 1 (10 runs), ring 2 (2 runs), and this
  full-coverage pass (4 runs).
- **Cadence going forward:** two full-suite passes after any build slice
  that touches `src/`, `tests/`, or an instrument (~110 s total); the
  sentinel stays excluded and runs on its own schedule.

— Kiln, R&D pulse 2026-09-12, ~15 min, $0.
