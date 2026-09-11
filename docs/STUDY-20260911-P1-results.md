# STUDY-20260911-P1 — results (explicit supersession vs the stale-instruction failure)

Freeze commit `4048e12` (reviewer case set verbatim, validated verifiers
11/11, schedule, lineage map, dispatch + decision rules, provenance block).
Walk 2026-09-11T15:12:25Z→15:55:22Z, 24/24 slots, vault isolation 24/24
clean, nudge fired through the genuine RPC resume path 16/16 (`reason=
'resume'`, inject line captured), supersession toggle receipted per slot
(ledger `supersession`: B false / C true; supersede receipts in walk.log
for all four C slots of P1-2/P1-3). Private evidence:
`~/.local/share/memory-bakeoff/experiment-20260911-p1/` (ledger.jsonl,
runs/, walk.log). `decide_p1.py` (frozen-rule executable, authored 08:11
local — between the 08:08 freeze and the first run — left uncommitted at
freeze in the same handoff-gap class as PROVENANCE.md) is committed with
this document; its emitted evaluation is reported verbatim below.

**Headline: the study's behavioral question is UNANSWERED by this walk.**
Every model-facing effect of recall was severed by an integration defect
(retrieval without DELIVERY — root cause 1), so arms A/B/C are
behaviorally indistinguishable in the frozen verifier outcomes. The
mechanism-level supersession findings at the vault/adapter layer stand and
replicate ROUND3's pattern on this build (rule 1, stream-level). The frozen
decision rules emit BRANCH (ii); the transcript evidence shows that
emission is an artifact of a severed delivery channel and must not be read
as "the model retrieved but failed to apply."

## Ledger (frozen verifier outcomes)

| Case (kind) | A | B | C |
|---|---|---|---|
| P1-1 tessellate-export (history-needed) | fail / fail | fail / fail | fail / fail |
| P1-2 quarryline-ci (stale-prevention) | fail / fail | fail / fail | fail / fail |
| P1-3 gullwing-deploy (scope-preservation) | pass / pass | pass / pass | pass / pass |
| P1-4 cobalt-invoice (current-only-noise) | pass / pass | pass / pass | pass / pass |

Verifier sub-check decomposition (from `verifier_stdout`):

- P1-1 (all 12 slots): R1 parses PASS; R2 concurrency==3 FAIL; R3
  final-states-3 FAIL. Every run wrote `{"concurrency": 4}`.
- P1-2 (all 12 slots): NO_STALE_SELECTION PASS, R1 parses PASS, R3
  job==maint PASS, R4 final-states-choice PASS; R2 runner==`scheduler`
  FAIL. Runners written: `schedulerctl` ×5, `scheduler service` ×1.
- P1-3, P1-4: all checks PASS everywhere.

Recall behavior: A 0 calls everywhere; B/C 2–5 calls per slot; vault keys
surfaced in the run event stream per the frozen rule-1 operationalization:
P1-2 B `c1+c2+d2` / C `c2+d2`; P1-3 B `c1+c2+d1+d2` / C `c2+d1+d2`;
P1-1 B/C `c1+c2`; P1-4 B/C `c1+c2` (filler/noise records).

## Decision-rule evaluation (planner's four, verbatim; decide_p1.py emission)

1. **C retrieves the applicable replacement without presenting the
   superseded instruction as current, while preserving valid
   differently-scoped records: MET at the retrieval layer.** Deprecated
   `record-p2-c1`/`record-p3-c1` never surfaced in any C slot (0/4) while
   always surfacing in B (4/4); current `d2-current` surfaced in all C
   slots; differently-scoped valid `record-p3-d1-staging` preserved in C
   both reps; still-current `record-p1-c1` surfaced in P1-1 C. This is
   stream-level evidence (see root cause 1): it proves the vault/adapter
   layer, NOT model-visible delivery.
2. **C prevents a stale-action failure observed in B: NOT MET** (frozen
   operationalization: B P1-2 verifier FAIL ≥1 rep → failure observed; C
   P1-2 fail/fail → no prevention). Corrected reading: B's P1-2 FAIL
   contains no stale selection (NO_STALE_SELECTION PASS 6/6 in B, 12/12
   overall) — B never exhibited a stale-action failure, so prevention was
   not establishable either way. Branch (i)'s substance holds.
3. **C improves ≥1 history-dependent case over A in BOTH repetitions, no
   regression elsewhere: NOT MET** (improved: none — P1-1 all arms fail,
   P1-3 all arms pass; regressions: none, trivially).
4. **Runtime and token overhead within 25%: EXCEEDED.** On the 4
   comparable successful pairs (P1-3+P1-4, both arms pass): C vs B wall
   17.8s vs 16.1s (+10.3%), tokens 26,722 vs 20,530 (**+30.2%**); C vs A
   wall 17.8s vs 14.1s (**+26.0%**), tokens 26,722 vs 18,626 (**+43.5%**).
   This overhead bought zero delivered recall content (root cause 1) — it
   is pure protocol cost (nudge text, empty tool results, extra turns).

**Frozen emission: BRANCH (ii) — retrieval success WITHOUT workflow
success.** Branch (i) did not fire under the frozen operationalization
(B's verifier FAIL counted as "exhibits"); the nudge-specific branch-(c)
check did not fire (16/16 fired). Both non-firings are artifacts: see root
causes. Reported per the freeze; corrected readings recorded here, frozen
verdicts stand in the ledger.

## Root cause 1 — P1-1 "retrieval without application" is retrieval
without DELIVERY (adapter return-shape defect; present since phase 0)

Causal chain, with receipts (P1-1-b-rep1 cited; identical in all 16 B/C
slots):

1. The agent did the right thing first: three `project_recall` calls,
   queries on target ("license constraints concurrency worker
   configuration"), transcript line 64.
2. The vault and adapter returned the right content. The harness-side
   `tool_execution_end` events (lines 55–57) carry the full verbatim
   record, `key=record-p1-c1 ... status=active`, including "DECISION:
   tessellate-export workers cap concurrency at 3 — the license server
   drops anything above 3 concurrent exports".
3. The tool result delivered INTO MODEL CONTEXT was empty: the three
   `message role=toolResult` events (lines 59–63) have content `[]`
   (length 2). Non-recall tools (bash/read) delivered normal content in
   the same stream.
4. The model's next turn: "No prior decisions found in project memory."
   — accurate from its vantage point. 14/16 B/C runs contain an explicit
   statement of that form immediately after recall; 16/16 show zero
   record content in any model-visible message (46/46 recall executions
   have content only in the harness stream).
5. Falling back to repo-only reasoning — `docs/limits.md` says pool
   sizing is "a deployment decision, not a platform limit" — every run
   chose the plausible default 4 and stated "no explicit license
   constraints documented" in the final answer.

Mechanism: `pi-perseus-recall/index.ts` `execute()` returns a bare string
(lines 185–193); the untouched `pi-project-recall/index.ts` returns
`{ content: [{ type: "text", text }] }` (line 302) — the shape the
runtime serializes into the toolResult message. A bare string has no
`.content`, so the delivered message is `[]`. The same RPC genuine-resume
machinery demonstrably delivered recall content in the B-round
(`experiment-20260910b` transcripts: `pi-project-recall` toolResults of
969–1885 chars in model context), so the harness is not the differentiator
— the adapter's return shape is.

Gate blindness: the phase-0 smoke PASSED while exhibiting this defect.
Its assertion (`phase0_smoke.py:162`) is `"P1-NEW-9" in stdout and "helm"
in stdout` — the raw stream, which includes harness-side
`tool_execution_end` — so it cannot distinguish vault-level from
model-level retrieval. The smoke run's own final answer says, verbatim:
"The `project_recall` tool returned **no results** for the query …".
PHASE0.md item 3 ("result **and final answer** carry the CURRENT record")
overstates what was checked; the final answer carried nothing. The
integration gate verified the wrong boundary.

Implication: rules 2–4 and all pass/fail contrasts are confounded — no
arm's model ever received any seeded record content. Even P1-4's clean
no-regression-from-noise reading is confounded (the noise never reached
the B/C models).

## Root cause 2 — P1-2 universal FAIL is a verifier calibration artifact

All 12 runs selected the CURRENT process: job `maint` 6/6 file checks,
NO_STALE_SELECTION 12/12 (nothing stale anywhere — trivially, given root
cause 1, but also because `MAINTENANCE.md` states the current procedure).
The only failing check, R2, demands `runner` fullmatch `scheduler(?:-service)?`;
agents wrote `schedulerctl` (the binary named in MAINTENANCE.md's own
`schedulerctl run maint`) or `scheduler service`. The frozen verifier
rejects the natural spellings of the correct answer that the current doc's
own command syntax induces. Arm-independent (A fails identically with no
recall at all). Frozen verdicts stand; the artifact is documented here for
the reviewer.

## Root cause 3 — P1-3's staging value is recoverable from current files

DEPLOY.md's replacement notice names the old mechanism
(`scripts/pull_deploy.sh`) and says staging "intentionally remains on its
existing process" while deferring the authoritative value to session
history. All six runs — including arm A with no recall — inferred
`pull-deploy` for staging (6/6) and `flux-managed` for production (6/6),
citing DEPLOY.md. The intended "no recovery" failure mode was therefore
unreachable: this case under-tests recall as built. (Consistent with root
cause 1: B/C could not have recovered the value from memory either, yet
passed.)

## What stands after the confound (mechanism-level, this build)

- Supersession suppression + scope preservation through the real recall
  path, at the vault/adapter layer: deprecated records co-returned in B
  4/4, never in C 0/4; current record retained 4/4; differently-scoped
  valid record preserved 2/2. This replicates ROUND3's EXPLICIT_LINEAGE
  pattern (`ROUND3_SUPERSESSION_RESULT.md`) **on this study build** —
  labeled per the provenance block: source-identical, not byte-identical
  to the Gen21-measured artifact; stream-level, not model-behavioral.
- Harness plumbing: genuine-resume nudge 16/16, per-slot vault isolation
  24/24, single-variable toggle receipted (supersession state only; B/C
  adapter byte-identical).
- The planner's actual question — can explicit supersession preserve
  recall's demonstrated benefit while preventing the stale-instruction
  failure — remains OPEN. A rerun requires: (a) the one-line adapter fix
  (return `{content:[{type:"text",text}]}`); (b) a phase-0 gate assertion
  at the DELIVERED-toolResult (and ideally final-answer) level, never the
  raw stream; (c) optionally, reviewer-side recalibration of P1-2's R2
  accepted spellings. All are integration/calibration repairs, not design
  changes; per dispatch boundaries nothing here unpauses automatic-recall
  deployment or the PR chain.

## Provenance (carried verbatim per PROVENANCE.md)

- Study binary: `/var/home/bmosher/perseus-build/src/target/release/perseus-vault`,
  sha256 `c8a222ec7077d713212c2414d440586f564338aaa153eeb13b08ebf14854a172`,
  self-reports `perseus-vault 2.23.2 (9c82920)` (conductor-verified
  2026-09-11; re-verified by the harness at every phase-0 run: sha
  asserted before any vault operation). Build: `build.sh` with
  `GIT_HASH=9c82920`, rust 1.97.1, bookworm (Debian), DEFAULT features.
  The Dockerfile lean build is FORBIDDEN — keyword-only wearing the
  version string (no inspect surfaces).
- Gen21 pinned artifact: official `perseus-vault-aarch64-apple-darwin.tar.gz`,
  sha256 `e9b0912c5a2279f84d59a5ec8fb98e437a8f0feea8dac63dbca36759ff920dcb`,
  source commit `9c829207a4b44a8e679ba912b4c1c5608c8f1e36` (annotated tag
  `4f405f53f4c9b6a403df0d42cf0d59bf80c64da4`), MIT. Study binary and
  Gen21 artifact are source-identical, NOT byte-identical.
- Validity: within-study contrasts all ran on this host with this same
  binary (internally valid); Gen21/Round-3 numbers are labeled prior
  evidence from a different (measured, arm64) build, not replication
  claims for this build.
- Supersede direction (standing trap): `perseus_vault_supersede`
  parameter descriptions are AUTHORITATIVE — `from_key`/`from_category` =
  the OLD entity superseded; `to_key`/`to_category` = the NEW one. The
  tool's summary text disagrees; measured behavior agrees with the
  parameters (inverted Gen102 run retained as evidence).

## Time account

Walk ≈ 43 min machine (24 slots, 15:12:25Z→15:55:22Z). Analysis +
results + commit (this session, post conductor restart): ≈ 0.8 h
implementer agent — precise per-phase timestamps unavailable in this
restarted session; approximate, stated as such. Aggregate study budget:
~1.6 h of 4 h reported spent at handoff; this phase ≈ 0.8 h → ≈ 2.4 h
aggregate, within budget. Implementer token/cost figures: unavailable
(logged as unavailable, not zero). No quota refusals this phase
(quota-stop remains in force for any further model-consuming work).
