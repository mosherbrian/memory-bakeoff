# P6-r13 candidate plan (kiln, P6r13-initial-1)
- New-core regressions: candidate/tests/test_r13_record_integrity.py (8 tests, A-E).
- Retained P5-r2 83: candidate/tests-retained/p5r2 (path inserts adapted to NEW core).
- Retained P3-r3 59: candidate/tests-retained/p3r3 (+ local cli.py ledger_packages shim; fixtures copied).
- R11 composed gate: candidate/tests (R11 42 files incl. rejection/routing) + candidate/stagec-plan.json.
- Proposed verify: pytest candidate/tests/test_r13_record_integrity.py,
  candidate/tests-retained/p5r2, candidate/tests-retained/p3r3 (fast);
  full candidate/tests composed gate (~23m) with PYTHONPATH=candidate/src.
