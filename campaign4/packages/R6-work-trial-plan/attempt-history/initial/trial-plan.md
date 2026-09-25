# R6 trial plan: paired memory/control feasibility comparison on the S13-2G gate repair

Design only. No run, code, harness, install, or model trial under this
contract. One implementable, preregistered comparison; a concrete no-go is
returned instead of an invented implementation if any prerequisite below is
unmet at authorization.

## Task and starting snapshot

The R4-selected repair: `team/S13-STATEUPD-AUDIT/check.py` (round-2
re-issue) repaired per `team/CORVID-S13-2G-VERIFY.md` §Fix 1–3, verified by
`check.py --selftest`, an honest-receipt probe, and the 27 named negatives.
Starting snapshot: `inputs/check.py` in this package, sha256 `8c921fbb…`
(byte copy of the working tree file; original untouched). At authorization,
re-verify the hash; on mismatch, stop (no-go: starting code changed).

## The comparison (paired pilot, one worker, two runs)

Same worker model, same task card including the full fix specification,
same repository access, same per-run time box (45 min: ≤20 min session 1,
≤25 min session 2). Run order (memory-first vs control-first) decided by a
recorded coin flip before either run starts.
- **Session 1 (both runs):** explore the gate, reproduce the failure on an
  honest receipt, attempt the fix. All work stays in ordinary files, which
  are preserved equally for both runs.
- **Boundary:** at session 1 end, record the runtime session ID and a
  sha256 inventory of the run directory; at session 2 start, record the
  same. The boundary holds iff inventories match (memory arm) or the
  memory dir is verifiably absent (control).
- **Session 2, memory run:** the seat additionally receives its own
  session-1 materials — attempts, notes, failure records written to the
  designated `memory/` directory (enumerated at the boundary record).
- **Session 2, control run:** starts from repository state plus the
  identical task card only; no prior-session materials. Control is denied
  nothing during any session; only cross-session retrieval differs.
- **Memory-only capability:** write/read of the seat's own prior-session
  materials via the `memory/` directory. Everything else (python3, git,
  gate file, reviews, model, prompts, time) is identical.

## Outcomes and checks (executed, not asserted)

Per run: (a) `check.py --selftest` exit code; (b) honest-receipt probe exit
code (genuine-mechanisms-only receipt must not raise
`CANDIDATE_SECTION_COUNT`); (c) the 27 named negatives still failing with
expected findings. Decided by running the check, never by inspection.
Inconclusive result: with one seen task, any outcome — including a memory
win — establishes only that the contrast is implementable, never general
efficacy and never a clean estimate (learning effects confound
within-worker pairing; both arms share the seen specification).

## Contamination and limits

The worker has read the fix specification (seen task); order randomization
mitigates but does not remove learning effects. Solution leakage through
the shared spec is unpreventable here and is disclosed, not denied. No
population or efficacy inference from this pilot. Null/incomplete runs are
reported as-is with preserved partials.

## Stop / no-go conditions

Stop and preserve partials on: starting-gate hash mismatch; selftest
already green at start (nothing to repair); time-box expiry; missing
boundary records. Concrete no-go (return, do not improvise): no runnable
python3/git; gate file absent; no blind outcome reader available for the
run records. Resource cap: 2×45 min worker runs + verification; no new
harness, install, or model trial.

## Next execution steps (each needs separate release)

1. Tern authorizes a run; worker records the coin flip and starting hashes.
2. Run 1 (allocated arm): session 1 → boundary records → session 2 with
   arm-appropriate materials → outcome checks executed.
3. Same for run 2 with the other arm. 4. Verifier checks hashes, boundary
   records, and check outputs against this plan. 5. Tern disposition.
