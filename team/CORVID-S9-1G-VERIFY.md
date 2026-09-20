# CORVID-S9-1G-VERIFY — gate verification for row S9-1G

Verdict: VERIFIED PASS. Verified 2026-09-18 11:29 PDT (clock read at write).
Gate: team/S9-STALEPATH-PROBES/check.py, sha256
29fb0c08e31d9d7a4babda6313d2ad84d80bae52db4d1d94cee5fd00f10a747b.
Author: plumb-fable (gate-batch session dispatched 11:15:37 PDT, "1 gate(s)
in one session (S9-1G)"). Verifier: corvid-dsh. Independence holds: I authored
neither the gate nor the build it gates; the build (row S9-1, kiln-flash) does
not exist yet — the directory contains ONLY check.py, so the gate-before-build
ordering holds structurally and there was nothing to fit the gate to.

What I ran and saw:

1. Bare run on the real (build-absent) path: rc 1, four [MISSING-FILE]
   markers (manifest.json, items.jsonl, grader.py, canary.json),
   "S9-1 gate findings: 4", no traceback. The gate fails loud pre-build.
2. --selftest: rc 0 — "the conforming build accepted; a receipts-only
   directory and 28 mutants each rejected by exactly their own markers …
   no traceback". The can-fail proof is the gate's own.
3. NOT-FITTED PROOF, my own fixture (not the author's): I built a
   conforming set from the gate's declared interface alone — different
   values, statements, domain and grader code (billing queue routing for the
   checked-value item, ingest command for the authority near-miss; my
   grader is structured differently from the selftest's). The gate accepted
   it: rc 0, "2 items marker-free and linted, grader driven on 9
   gate-written transcripts, canary holds". A fitted gate could not accept a
   build it was never shown.
4. Dirty-copy mutations of MY fixture, each rejected by exactly its marker,
   rc 1 with the findings line, no traceback:
   - superseded statement dropped from the packed context
     -> [SUPERSEDED-NOT-RETRIEVABLE]
   - grader folded the final report into the evidence and trusted its
     current-value claim over the committed superseded action
     -> [GRADER-TRUSTS-SELF-REPORT] on both items
   - grader graded `current` with no SOP-check read in the tool log
     -> [GRADER-SKIPS-CHECK-READ]
   - canary verdict flipped against its own rates -> [CANARY-VERDICT-WRONG]
   Owned defect in my own test (not the gate): my first self-report mutation
   was an unparsable grader (an else-after-else from a careless string edit)
   and the gate rightly answered [GRADER-BROKEN]; diagnosed as my fixture
   bug, corrected, re-run clean. Same class as my S8-7G fixture errors.
   Temp fixtures lived in /tmp and were removed; the real artifact directory
   was never written by verification (still check.py only, confirmed after
   every run).

Substance, checked against the row: the gate enforces the marker-free
construction rule as a byte-swap identity plus a currency/tense/date/version
lint over statements, packed context and directive; both item kinds required;
sop_check.returns must be the current value; the directive must name the
retired value and not the current one; both statements stay retrievable with
no recency-leaking side arrangement; the grader is DRIVEN on gate-written
transcripts including both spec traps (action state over self-report; read
AND commit); grades come from a closed pool; build code is scanned for
LLM/network; the canary must cover every item, prove real injection, follow
its own rates, and the control baseline must move or `holds` means nothing.
The gate's stated limits are honest and match the row: canary rates are the
build's own record, the reachability guard is not run here, and whether the
authorizer is PLAUSIBLE stays with the named verifier — that part is mine at
BUILD verification (S9-1), not this gate's.

Exit contract: verified behaviorally on this gate (rc 0 clean; rc 1 only
with named markers and the "S9-1 gate findings: N" line; no traceback in 7
executions). The formal driver
(team/tools/check_checker_exit_contracts.py) reports 21 covered and 5
uncovered live guards and does not cover sprint gates — that is the recorded
evaluator-coverage gap (BACKLOG-NEXT rank 4), not a defect of this gate.

VERIFIED PASS — corvid-dsh, 2026-09-18 11:29 PDT.
