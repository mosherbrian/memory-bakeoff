# R51 readiness (offline; zero model calls)

**Corrected.**
- scan.py v4 (diff: scan.py.diff vs R50). A tool_use with neither a result nor a denial is UNRESOLVED: its paths are unconfirmed and it makes the arm ambiguous, never clean or contaminated. A denial is recognised with or without the usual is_error result. A denial plus a NON-error result is contradictory: the call is treated as possibly executed and flagged. Precedence: confirmed forbidden access -> contaminated; any unresolved, contradictory or other ambiguity -> ambiguous; else clean.
- operator/scan_gate.py wraps every scan with a 60 s timeout. It validates that the output is a JSON object, the status is known, the required typed fields are present and the exit code agrees. Timeout, invocation failure, crash, empty or non-JSON output, unknown status, missing fields, rc mismatch and scanner_error all give `evaluator_failure` (exit 5), never clean or contaminated.
- Integration: operator/run-arm.sh (diff: operator/run-arm.sh.diff vs R49) calls scan_gate for s1 and s2, writes scan-gate-s{1,2}.json, and HOLDS the arm (fail -> wake Tern) on exit 5.

**Tests.** tests/run_tests.py -> tests/results.json: 35/35 as expected. 10 new outcome cases; 14 R50 regressions unchanged; frozen R49 A-N s1 and s2 = clean (labelled reanalysis; R49 raw primary false, attempted restore, no memory, all unchanged); 9 gate failure modes all evaluator_failure.

**Limits.** Heuristic shell parsing; same-user obfuscation; manual review of every tool event remains required. The proposed run-arm.sh still names the R48 launcher/templates; a new cohort must point it at the R50 launcher and templates (argv capture, one-command line) before use.

**Smallest next step.** Tern's decision on the one-arm new-cohort qualification proposed in R50 (2 Max calls), using the R50 launcher/templates and this gate.
