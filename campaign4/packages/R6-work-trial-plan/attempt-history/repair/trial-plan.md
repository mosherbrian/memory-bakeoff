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
  same. Runtime sessions are the existing agent-deck seat sessions
  (registry IDs with socket identity, e.g. `a79067ca-1790000758` in
  campaign dispatch receipts) — named existing capability, no new
  harness. The boundary holds iff inventories match (memory arm) or the
  memory dir is verifiably absent (control).
- **Session 2, memory run:** the seat additionally receives its own
  session-1 materials — attempts, notes, failure records written to the
  designated `memory/` directory (enumerated at the boundary record).
- **Session 2, control run:** keeps every ordinary file both runs share,
  including anything the seat wrote in session 1; the designated `memory/`
  directory is absent. Control is denied nothing during any session; only
  cross-session retrieval of prior-session materials differs. There is no
  control reset: ordinary workfiles persist equally in both runs.
- **Memory-only capability:** write/read of the seat's own prior-session
  materials via the `memory/` directory. Everything else (python3, git,
  gate file, reviews, model, prompts, time) is identical.

## Outcomes and checks (executed, not asserted)

Per run: (a) `check.py --selftest` exit code (informational: it passed on
the broken gate, so green selftest alone proves nothing); (b) honest-receipt
probe — receipt fixture `inputs/honest-receipt.md` (construction rule
below) run as `check.py --root <repo> --receipt <fixture>`, expected exit 0
with no `CANDIDATE_SECTION_COUNT`; (c) the 27 named negatives still failing
with expected findings; (d) negative commands: `check.py --bogus` (exit 1,
argument finding) and a missing-receipt invocation (exit 1, receipt-missing
finding). Decided by running the check, never by inspection.

### Honest-receipt fixture (hand-declared, never gate-generated)

`inputs/honest-receipt.md` is authored by hand from the review's genuine
set — never by running the gate's `inventory()`/`discover_candidates()`,
which would repeat the flawed discovery logic. Sections (one disposition,
every card filename cited): the gate's own BASE four (agentmemory,
Hindsight, Mem0, MemPalace) plus card-labeled products verified from
headings (Engram Alpha as labeled system; mex, Munder Difflin, Procedural
Graphs as products). Explicitly excluded as non-mechanisms: the `External
benchmark`/`External system` heading prefixes, `TEAM RECOMMENDATION`,
date-coded filename stems, and generic/technology words. Further product
identities (Zep, Letta, Supermemory, Heimdall) enter only with a
card-explicit System:/Product: label recorded; otherwise excluded by the
same rule. If the repaired gate demands sections beyond this declared set,
that mismatch is recorded as a finding against the repair — never silently
satisfied by fabrication.
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

Stop and preserve partials on: starting-gate hash mismatch; time-box
expiry; missing boundary records. An already-green selftest at start is
NOT a stop condition (established: green selftest passed on the broken
gate); the honest-input failure evidence is the review's reported probes
(round-1 inventory returning 12 names incl. 4 non-mechanisms; round-2
returning 73 names), cited as reported evidence and explicitly declared
as not independently re-executed. Concrete no-go (return, do not
improvise): no runnable python3/git; gate file absent; no blind outcome
reader available for the run records. Resource cap: 2×45 min worker runs
+ verification; no new harness, install, or model trial.

## Next execution steps (each needs separate release)

1. Tern authorizes a run; worker records the coin flip and starting hashes.
2. Run 1 (allocated arm): session 1 → boundary records → session 2 with
   arm-appropriate materials → outcome checks executed.
3. Same for run 2 with the other arm. 4. Verifier checks hashes, boundary
   records, and check outputs against this plan. 5. Tern disposition.
