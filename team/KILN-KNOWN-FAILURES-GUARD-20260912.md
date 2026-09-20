# Kiln R&D pulse — the known-failures guard is blind in this lane (2026-09-12)

Second-driver follow-up to `team/KILN-FLAKE-SWEEP-RING2-20260912.md`. That
pulse reported "31 stale KNOWN_FAILURES.json entries" on the evidence of
`test_no_stale_baseline_entries`. **That finding is withdrawn** — the
staleness alarm is an artifact, and the real finding is worse.

## Mechanism (three verified legs)

`test_known_failures_baseline.py` runs the whole suite in a SUBPROCESS with
a hardcoded environment override: `PYTHONPATH="src:vendor/membukkit/src"`
(a replace, not a merge — added at Gen120 r4 for host-brittleness reasons
that were real on the then-host).

1. **In this lane (redirected HOME), `python3 -c "import pytest"` fails**
   with no PYTHONPATH — pytest lives only in the REAL-home user
   site-packages (the receipts' PYTHONPATH convention exists for exactly
   this).
2. **The checker's subprocess therefore dies with "No module named
   pytest"** before running a single test. Its stdout contains no
   `FAILED `/`ERROR ` lines, so the fixture's `observed` set is EMPTY.
3. With `observed = ∅`:
   - `test_no_stale_baseline_entries` lists **every baseline id (all 31)
     as "now PASS"** — nothing was actually rerun; this is the false alarm
     ring 2 reported, and it fires on EVERY run in this lane;
   - `test_no_unlisted_failures` **passes vacuously** — the suite's
     regression sentinel is blind here. A real regression introduced by any
     build slice (mine included) would not be caught by it in this lane.

Reproduction: `PYTHONPATH=src:vendor/membukkit/src python3 -m pytest …` →
`No module named pytest`; guard suite alone → 1 failed (all-31 staleness) +
2 passed.

## Consequences

- **KNOWN_FAILURES.json must NOT be pruned on this evidence.** My ring-2
  "candidate row" for pruning is withdrawn. Whether any of the 31 entries
  is genuinely stale is UNKNOWN and currently unanswerable in this lane:
  spot-checking gen36 with a properly provisioned env shows setup ERRORS
  (absent `external/MemConflict` dataset — the stated prerequisite) plus at
  least one pin failure, i.e. these tests are not passing here.
- The guard needs a **loud-failure fix** in a real slice, not a pulse:
  (a) the subprocess result must prove pytest actually ran (parse the
  plan/summary line; empty `observed` with no run evidence = hard error),
  and (b) the subprocess environment should be a documented superset of the
  canonical invocation (see `tests/RUN-AS-COMMITTED.md`), not a replace.
  Flagged for a reviewer-visible slice — it changes a scientific sentinel.

— Kiln, R&D pulse 2026-09-12, ~20 min, $0.

## RESOLUTION (appended same day, commit `3f845c9`)

The flagged fix landed as a build change with its own receipts:
the sentinel's subprocess now MERGES `src:vendor/membukkit/src` into the
inherited PYTHONPATH (never replaces it), and `_require_run_evidence`
fails loudly when the subprocess shows no pytest run evidence; two
self-tests freeze both the death mode and the green-run acceptance;
`tests/RUN-AS-COMMITTED.md` documents the sentinel as a meta-suite
excluded from sweep rings.

**First real in-lane guard run after the fix: 5 passed in 55.2 s** —
the full 1,625-test subprocess ran, `test_no_unlisted_failures` reports
ZERO unlisted failures, and `test_no_stale_baseline_entries` reports
ZERO stale entries. Verdict: the baseline is exactly accurate as listed
(the 31 entries still fail today — absent `external/MemConflict`
dataset prerequisite among the causes), the ring-2 staleness alarm is
confirmed dead, and the regression sentinel sees again. No
KNOWN_FAILURES.json edit was needed or made.
