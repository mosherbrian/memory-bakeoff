# Validation tranche — 20 unseen files, frozen prompt

Seed 20260920, drawn from 747 files after excluding all 80 already-reviewed (20 difficult + 60 tranche). Prompt frozen at `35269fddefe0`, extractor `stage1/2026-09-19f`. No tuning between the draw and this report.

20/20 ok, zero rejected quotes, one first-attempt parse failure recovered by the single retry.

## Role distribution

- `verification` — 17
- `decision_record` — 7
- `proposal` — 5
- `implementation` — 3
- `measurement_report` — 2
- `research_intake` — 2
- `operations` — 1
- `synthesis` — 1
- `other` — 1

---

## ALICE-HINDSIGHT-AMB-REDERIVE.md
*A verification document that re-derives Hindsight's marketed benchmark scores (94.6/92.0) from raw per-question data shipped by the AMB benchmark and explains why the vendor's technical report shows a different figure (91.4).*

- **verification** (L20) — "The 2026 marketing **94.6% / 92.0%** are exactly the AMB harness runs, and the raw per-question data is published."
- **decision_record** (L56) — "Hindsight's marketed row upgrades to `vendor-only (independently recomputed from shipped raw rows)` for the AMB 94.6/92.0 — the same upgrade Memobase and agentmemory got."

  uncertain: Whether the ledger row upgrade has been formally accepted or is being recorded here as a consequence of this verification.

## ALICE-LETTA-685-PROPAGATION-FIX.md
*A post-resolution propagation fix document by Alice recording which current-state cells still carried a pre-resolution status after the D2 resolution, which were fixed, and which were flagged to the map owner.*

- **verification** (L11) — "The D2 resolution (Letta's "Mem0 68.5%" = Letta-side one-decimal mis-round of the paper's 68.44; no Mem0 artifact located states 68.5) had left **three current-state cells** still carrying the pre-resolution status."
- **implementation** (L37) — "I edited only my own authored files (ledger PROVENANCE section, collision register); the map is left to its owner."

  uncertain: ROLE: verification

## ALICE-S4-LIVE-LEAK-CENSUS-SECONDCHECK.md
*A second-seat verification check in which Alice independently rebuilt live worker-pi packets and compared scanner outputs against a prior S4 leak census document.*

- **verification** (L13) — "**PASS / AGREE on the substance and every session-level number** — an independent live rebuild reproduces 8 canonical findings / 4 sessions and 24 guarded findings / 1 guard-only session."
- **measurement_report** (L45) — "So `guarded = canonical(3 with values) + 21 value-only`, and `canonical = those 3 + 5 word-only`."

  uncertain: ROLE: verification

## ALICE-SUPERMEMORY-CLAIM-CHECK.md
*A claim-check document by Alice (verification/provenance seat) examining whether Supermemory's LongMemEval 95.0 score is traceable and whether its self-run harness allows the subject to override the judge prompt.*

- **verification** (L0) — "So the number OmniMemEval cites is **not currently traceable** — a dangling citation, whether from removal or a routing bug."

  uncertain: ROLE: verification

## ASSAY-MISSING-PREREQ-SUITE-SECONDCHECK.md
*This document is an independent second-seat verification of a suite-wide missing-prerequisite fix, recording that all claimed checks were reproduced and noting one residual boundary finding where a present-but-unreadable file still produces a traceback.*

- **verification** (L5) — "**Verdict: PASS / AGREE** on every claim made, plus one residual boundary finding (low) that the fix does not cover."
- **proposal** (L44) — "Recommendation (owner Corvid, optional): treat `os.access(p, os.R_OK) == False` after `.is_file()` as a structured `unreadable prerequisite: <relpath>` finding, or wrap `read_text`."

  uncertain: I could not tell whether the recommendation to handle unreadable files was subsequently acted upon.

## CANDIDATE-CARD-STATEMEMBENCH.md
*A candidate card assessing the external benchmark StateMemBench (arXiv:2608.19652) against internal goals G1–G5, produced by a proposal-drafter seat during a Phase-B frontier harvest.*

- **research_intake** (L0) — "Card 6 of the named benchmarks in `RESEARCH-INTELLIGENCE-DIRECTIVE.md`, assessed against our goals G1–G5 (`CORVID-INTELLIGENCE-DIRECTIVE-ASSESSMENT.md` §4)."
- **verification** (L79) — "Existence, ID, scale, and design claims **confirmed full-text (HTML) level**."
- **proposal** (L72) — "If the generator shape transfers, adapt only the **fixed-by-construction supersession probe** to our case-authoring guide (design, not a run)."

  uncertain: The referenced directives (RESEARCH-INTELLIGENCE-DIRECTIVE.md, CORVID-INTELLIGENCE-DIRECTIVE-ASSESSMENT.md) are not included, so the full scope of the intake mandate cannot be confirmed.

## CORVID-EXTERNAL-CORPORA-VERIFY-TRIAGE.md
*A verification and sprint-lane triage report on external corpora sources cited in a deep research report, authored by Corvid on 2026-09-13.*

- **verification** (L31) — "**VERIFIED EXACTLY** (67,074 and ~64 turns match)."
- **proposal** (L73) — "Sprint 2 goal 5 is the Phase-B-style harvest (owners Corvid + Alice, candidate discovery only). Lanes, in execution order:"

  uncertain: It is not clear whether the proposed sprint lanes (L1–L7) have been accepted or remain pending.

## CORVID-MEMTX-PINCHECK.md
*A pin check verifying that the claims in a candidate card for arXiv:2607.23929v2 match the paper's abstract page.*

- **verification** (L43) — "The card is accurate at the pin and abstract level and honestly classifies its numbers as vendor."

  uncertain: Whether this check resulted in any disposition of the card (acceptance, rejection, or update) is not stated.

## CORVID-ROW36-REACHABILITY-GUARD.md
*This document describes a reachability guard script written to check invocation-corpus `topic_reachable` labels against a binding trigger, and records its self-test and live-verdict execution outcomes.*

- **implementation** (L5) — "Artifact: `implementer/repo-glm-dsh3/scripts/check_invocation_corpus_reachability.py`"
- **verification** (L0) — "scenarios=12 findings=1 unreachable-topic: S09: manifest topic_reachable=True but binding trigger                    reachable=False (matched=[])"
- **decision_record** (L6) — "adopted as **guard 18** on 2026-09-14"

  uncertain: ROLE: implementation

## CORVID-S8-1G-VERIFY.md
*A close-on-evidence receipt for row S8-1G, recording that the duplicate gate is closed on existing evidence rather than by authoring a new gate.*

- **verification** (L11) — "Declared artifact `/home/bmosher/memory-bake-off/team/S7-BM25-PREFILTER/check.py` exists."
- **decision_record** (L6) — "Per cairn's ruling there is no gate to author for a re-run that will not happen; the row closes on evidence as written."

  uncertain: ROLE: verification

## CORVID-S8-4-VERIFY.md
*This document is a close-on-evidence receipt for row S8-4, recording its closure as a verbatim duplicate of S7-4 based on existing verification evidence.*

- **verification** (L12) — "Declared check re-run at close: `python3 team/S7-KD-WORLDS/check.py --selftest` → rc 0"
- **decision_record** (L18) — "This receipt books the duplicate's closure on existing evidence; it authors no new measurement."

  uncertain: I could not tell what "cairn" refers to as an authority or system, or what the "re-measurement rule" specifically requires.

## FLEET-SPEND-20260914.md
*A Rev 2 document reporting measured API spend, cache behavior, and rate tables for a fleet of 13 lanes on OpenCode Go, with a team decision on cost-reduction measures.*

- **measurement_report** (L42) — "Spend since 16:21 | **$5.90** (recorded) over 4.6 h, 2,970 billed calls"
- **decision_record** (L288) — "Apply 1+2+3 now; test 6 in parallel and prefer it if it holds; hold 4 in reserve."
- **synthesis** (L205) — "The dsh seats did **more calls on 2% of the fresh input** and produced 3× the output per call."

## KILN-D-8-VERIFY-20260919.md
*A verification report by kiln-flash checking the claims of a 14:01:38 restock instance authored by corvid-dsh against current file bytes and re-run probes.*

- **verification** (L3) — "Verdict: VERIFIED PASS, with one finding recorded (post-stamp artifact drift, disclosed inline, substantively TRUE; record-keeping gap, dispositions unaffected)."

  uncertain: ROLE: verification

## KILN-REDERIVE-AGENTMEMORY-929.md
*This document is a second-driver re-derivation that verifies previously reported agentmemory numbers (92.9% false supersession and reader correctness counts) against a frozen artifact's trace.*

- **verification** (L28) — "Verdict: **verifies**. The dimension is safe to keep traveling beside agentmemory's BAR B numbers."

## KILN-REDERIVE-CLAUDEMEM-WINDOW.md
*A second-driver re-derivation that recounts the Claude-Mem window ablation values from cited artifacts and checks them against the RESULTS.md row.*

- **verification** (L36) — "Verdict: **verifies**, direction and mechanism; one compression noted."

  uncertain: ROLE: verification

## PROBE-row6-admission-unit-tests.md
*A receipt from a worker seat reporting the results of running admission-path unit tests in a container and a corrected public-tool run that closed a gap in an earlier probe.*

- **verification** (L5) — "Verdict: PASS — 37 test executions, 36 unique, 0 failed, 0 ignored."

  uncertain: ROLE: verification

## RETRO-2-fsync.md
*A sprint retrospective for a seat called "fsync" (watch + receipt auditor) covering morale, effectiveness, and process recommendations for the next sprint.*

- **decision_record** (L25) — "Retire the Spark harvest seat to event-driven/resume-triggers permanently (already proposed in SPARK-SEAT-SATURATION-20260914.md; the week's evidence supports it: 50+ notes, then nothing but receipts)."
- **proposal** (L20) — "Event-driven watch: tick only on queue/board state change or elapsed-time threshold with new information; otherwise update a live state line."
- **operations** (L24) — "Keep this seat as frozen-instrument guard + receipt auditor, with the watch made event-driven per above."

  uncertain: It is unclear whether the role changes stated in section 5 (e.g., retiring the Spark seat) are formal decisions adopted by the fleet or recommendations pending acceptance.

## S9-DOOR-RUNG2/declaration.json
*A JSON declaration file specifying scoring criteria, a character budget, pressure metrics, and adapter names for a retrieval or scoring configuration.*

- **other** (L5) — ""presence": "all-helpful-substrings","

  uncertain: It is not clear from the text alone what system or pipeline this declaration governs, or whether it is operative or merely a snapshot of parameters at a point in time.

## SCALE-GATE-DRYRUN-I-SAID.md
*A scale dry-run report of an outcome export+gate process that identified a vocabulary gap (`i_said` class) and implemented an exclusion flag to resolve it.*

- **verification** (L16) — "Gate result: **FAIL**, findings 10× `bad class: 'i_said'` + 10× `bad subtype: 'i_said'` (nothing else)."
- **implementation** (L60) — "The exporter gained an auditable `--exclude-class` flag (default none)."
- **proposal** (L24) — "Two consistent ways forward, owner's call (spec = Assay, pipeline = Kiln, row-41 verifier = Cairn):"

  uncertain: Whether the owner has yet chosen between the two options (add to vocabulary vs. exclude before export) is not stated as a final decision.

## SPARK-COMPACTION-CLIFF-ARTIFACT-20260915.md  *[retried]*
*A follow-up note that resolves an open artifact row from a prior pincheck by locating and characterizing an external dataset and code repository (CIKM 2026).*

- **research_intake** (L3) — "Resolves the open artifact row in `CORVID-COMPACTION-CLIFF-PINCHECK.md` ("announced, no link located") and confirms Corvid's number correction"
- **verification** (L19) — "Direct fetch proves it: root `LICENSE` exists (HTTP 200) with Apache-2.0 text"
- **decision_record** (L0) — "No score import; no download taken this pass."

  uncertain: Whether the 'Brian/GiLMore call' for DUA signature has been executed or remains pending.

