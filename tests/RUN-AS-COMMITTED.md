# RUN-AS-COMMITTED (unit/contract suites)

Canonical invocation on this host (lane HOME redirect; pytest lives in the
REAL-home user site-packages):

    PYTHONPATH=/home/bmosher/.local/lib/python3.14/site-packages python3 -m pytest tests/<suite> -q

- Receipt-bearing suites: `test_pi_lcm_store_reader_contract.py` (12),
  `test_longcontext_null_contract.py` (7), `test_stale_use_penalty.py` (8),
  `test_agentmemory_core.py` + `test_agentmemory_localization.py` (13).
- Flaky-adapter sweep (2026-09-12, `team/KILN-FLAKE-SWEEP-20260912.md`):
  9 suites / 82 tests green across sequential, PYTHONHASHSEED and
  reversed-order axes; ~25 s per sweep. One pass per provider-touching
  build slice.
- Suites needing external services or metered lanes are out of this
  convention's scope; they run behind their own receipts.

## Meta-suite note (2026-09-12): tests/test_known_failures_baseline.py

This file is a SENTINEL, not a sweep subject: its fixture re-runs the whole
suite in a subprocess and compares failure ids against
`tests/KNOWN_FAILURES.json`. Exclude it from flake-sweep rings (a sweep
would trigger a full-suite run). It needs the canonical PYTHONPATH above —
its subprocess now MERGES `src:vendor/membukkit/src` into the inherited
PYTHONPATH and fails loudly when the subprocess shows no pytest run
evidence (previously it replaced the path, died pre-import in
redirected-HOME lanes, and passed vacuously; see
`team/KILN-KNOWN-FAILURES-GUARD-20260912.md`).
