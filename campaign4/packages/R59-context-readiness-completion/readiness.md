# R59 context-trial runner: readiness

Result: all 22 rows in requirements-evidence.json have test evidence from the ACTUAL runner (operator/run-arm.sh), run offline with stubs (tests/run_tests.sh -> tests/results.txt, bundles in tests/evidence-stub/). The requirement file was committed before the code.

Repairs of R58 gaps:
- G1 parent project / memory preflight: zero calls, HOLD, evidence frozen (1a, 1b). Realpaths recorded (1c).
- G2 R54 events.py now runs on every available transcript, on every exit path; flags and evaluator failure are HOLDs (2a-2c).
- G3 memory snapshots copy real files; ABSENT vs EMPTY_DIR; boundary change detected, not repaired (3a-3d).
- Failure paths: s1/s2/D non-zero, missing exit metadata, timeout 124, kill 137, gate 1/2/3/5, R57 manual flag - all HOLD (4a-4g).
- Every stop path freezes one atomic, hashed, non-overwritable bundle; missing standard files are listed, not invented (5a, 5b). Duplicate label stops before any side effect (5c).
- Test seams are refused unless STUB_BIN is set, DRY=1 and the stub is not the real claude (4h).

Limits (stated, not hidden):
- No live launch was made (as released). Stubs prove control flow, not real Claude Code behaviour.
- Stub transcripts have no tool uses, so events.py ran only on trivial transcripts; its own logic is R54's frozen evidence.
- Realpath recording was not exercised through a symlink.
- R57 grading is always manual under stubs (no report written), so a clean automatic grade path was not exercised here.
- Frozen dependencies (R56 launch/fixture/scanner, R57 grade.py, R54 events.py) are unchanged; each bundle pins their hashes.

Diffs vs R58: tests/diff-vs-R58-run-arm.diff, tests/diff-vs-R58-freeze.diff.
