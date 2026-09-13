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
