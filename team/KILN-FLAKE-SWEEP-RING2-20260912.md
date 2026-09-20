# Kiln R&D pulse — flake sweep, ring 2 (2026-09-12)

Extends `team/KILN-FLAKE-SWEEP-20260912.md` (ring 1: 9 suites / 82 tests)
with a second ring: 36 pure-logic suites by name-class — scorers, semantics,
temporal/supersession logic, scope/configuration bounds, gates, and the
record-hygiene checks — still excluding anything service-gated, metered,
process-spawning, or live-state. $0, no live-window contact.

## Result

**384 tests, 2 runs: 383 passed + the SAME 1 failure both times**
(deterministic, not a flake), wall 3.5–3.6 s per run. Sweepable universe
grows: ring 1 + ring 2 = **466 tests**, all stable under repeat.

## The one failure is a hygiene alarm, not a bug

`tests/test_known_failures_baseline.py::test_no_stale_baseline_entries`
fails because **KNOWN_FAILURES.json has drifted upward**: 31 entries are
listed as known failures but now PASS (2 × gen119_run_apparatus,
8 × membukkit_gen41_round1 device-pin params, 8 × memconflict_gen36_contract,
6 × gen37_products, 7 × gen38_full_release — all "pins unchanged /
reconciles / deterministic" integrity tests). The suite's own message says
what to do: prune them so the baseline cannot drift.

**Deliberately NOT reconciled in this pulse.** Editing KNOWN_FAILURES.json
is a record-level change with scientific-semantics baggage (reset plan §7:
match by actual test identity and cause; the R1 reconciliation already
touched this file once). It deserves a dedicated, reviewer-visible slice —
flagged here as a candidate row, with this note as the evidence. Caveat
stated: I did not independently rerun the 31 tests; the baseline suite's
own finding is the evidence.

## Sweep state after ring 2

| Ring | Suites | Tests | Status |
|---|---|---|---|
| 1 (2026-09-12 AM) | 9 | 82 | green × 10 runs, 0 flakes |
| 2 (this pulse) | 36 | 384 | 383 green × 2 runs + 1 documented stale-baseline alarm |
| Remaining out-of-scope | ~77 files | ~1,159 | service/metered/live/process gates unlabeled (see coverage map) |

Cadence proposal stands: one sweep pass (both rings, ~6 s) per
provider- or runner-touching build slice.

— Kiln, R&D pulse 2026-09-12, ~15 min, $0.

## CORRECTION (same day, second pulse — superseded by
`team/KILN-KNOWN-FAILURES-GUARD-20260912.md`)

The "31 stale KNOWN_FAILURES.json entries" above was a **false alarm** and
the candidate pruning row is **withdrawn**. The staleness checker's
subprocess cannot import pytest in this redirected-HOME lane (its hardcoded
`PYTHONPATH` replace drops the real-home site-packages), so it observes an
empty failure set and lists the ENTIRE baseline as "now PASS" on every run.
Nothing was rerun; nothing is proven stale. The load-bearing finding is the
opposite one: `test_no_unlisted_failures` passes vacuously here — the
suite's regression sentinel is blind in this lane. Ring 2's sweep numbers
(384 tests, 383 green) remain valid; only the staleness interpretation is
withdrawn.
