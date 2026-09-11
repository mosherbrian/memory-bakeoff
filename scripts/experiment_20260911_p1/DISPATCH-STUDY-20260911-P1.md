# DISPATCH — STUDY-20260911-P1: explicit supersession vs the stale-instruction failure (planner-directed, Brian-funded 2026-09-11)

Question (planner's wording): **Can explicit supersession preserve recall's
demonstrated benefit while preventing the stale-instruction failure?**

Context: EXPERIMENT-20260910B/C verified that nudged cross-session recall
recovers lost decisions (H1) but takes stale actions when history is
superseded (S1; mitigation wording insufficient, ~2x overhead). Perseus
(`EXPLICIT_LINEAGE`) demonstrated exactly the needed retrieval behavior in the
original bakeoff — canonical account: ROUND3_SUPERSESSION_RESULT.md ("works
completely, at no cost": stale co-return removed 48/48 cells, current record
lost 0). Mind the documented trap: the supersede tool's summary vs parameter
descriptions disagree on `from_key` direction — PARAMETERS ARE AUTHORITATIVE
(measured behavior agrees); the inverted run is retained as evidence.

## Phase 0 — integration checkpoint FIRST (<=45 min, inside budget)

Prove, through the ACTUAL harness path (RPC genuine-resume machinery from
B/C-rounds), all three:
1. the existing Perseus adapter runs as a Pi recall path;
2. supersession toggles cleanly between two otherwise-identical configs;
3. the coding agent retrieves a known replacement through the real path.

STOP AND REPORT at the conductor gate. If any of this requires substantial
reconstruction, return the CONCRETE OBSTACLE before spending the remainder of
the budget. Do not proceed to case preparation before the gate passes.

## Arms (planner table, verbatim intent)

| Arm | Configuration | Purpose |
|---|---|---|
| A | Pi-LCM alone | Practical baseline |
| B | Pi-LCM + Perseus recall, supersession DISABLED | recall with both old and current records available |
| C | Identical to B, supersession ENABLED | isolates the contribution of supersession |

B and C MUST be identical in tool descriptions, nudges, queries, retrieval
limits, and seeded records — ONLY supersession handling changes (single
variable, verified at code + as-loaded receipt level as in C-round). Both B
and C receive the SAME current decision (no information confound).
Replacement relationships are supplied EXPLICITLY before execution — label
the study "supersession given correct lineage" (discovery is a separate
capability, out of scope). No fourth arm.

## Slots: 4 fresh cases x 2 reps x 3 arms = 24 (planner's case set)

1. historical knowledge needed, NO supersession (benefit);
2. obsolete procedure replaced by a current procedure (stale-action prevention);
3. replacement applying to ONE environment while the old decision remains
   valid in ANOTHER (scope preservation);
4. task fully specified by current files, distracting history available
   (unnecessary recall/noise).

Reviewer authors cases blind to arms, per house convention. VERIFIER RULE
(planner, verbatim intent): verifiers assess artifacts and actions, and MUST
explicitly permit quoting obsolete instructions when explaining their
rejection — the mention-vs-selection distinction that tripped the C-round
frozen heuristic. The reviewer VALIDATES that distinction against synthetic
positive/negative outputs BEFORE the freeze commit.

## Success = mechanism AND practical (planner's four, verbatim)

1. C retrieves the applicable replacement without presenting the superseded
   instruction as current, while preserving valid differently-scoped records.
2. C prevents a stale-action failure observed in B.
3. C improves >=1 history-dependent case over A in BOTH repetitions, no
   regression elsewhere.
4. Runtime and token overhead within 25% where comparable successful pairs
   exist; insufficient comparisons remain UNRESOLVED (state it, never guess).

Predeclared distinct-outcome branches: (i) B never exhibits the failure ->
study CANNOT establish prevention (report as such, not as success);
(ii) C suppresses stale records but fails the task -> retrieval success
WITHOUT workflow success (report as distinct outcome). Branch (b/c/d)
conventions as prior rounds; freeze ALL rules before any run.

## Budget + stop rules

- 4 aggregate agent-hours TOTAL (integration, case prep, review, execution,
  reporting), 4h machine occupancy.
- GLM quota refusal = stop-and-report immediately.
- Stop-before-evaluation if prep overruns; report, never expand.

## Boundaries

Automatic-recall deployment stays PAUSED during this study; PR chain stays
halted; pi-project-recall/ and pi-recall-nudge/ untouched (Perseus work is a
separate adapter path); F1/F2/f3 and B/C-round records untouched (new results
doc section only). Workers remain available afterward.

## Sequencing

Phase 0 checkpoint -> conductor gate -> reviewer authors cases (+verifier
distinction validation) -> freeze commit (cases + verifiers + schedule +
lineage map + decision rules) -> conductor gate -> walk -> analyze ->
reviewer verification -> package to Brian. Self-chaining note: once a gate
passes, the implementer chain runs to report without further conductor hops
(overnight-pause lesson, 2026-09-11).
