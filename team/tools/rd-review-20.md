# Stage-one review set - 2026-09-19

Every quote below has been verified to appear in its file. That is PROVENANCE, not correctness: what needs your read is whether each ROLE is the right one for the sentence supporting it.

## ALICE-MUSE-BATCH5-SECONDCHECK.md
*A second-seat verification check of Muse batch 5 (MUSE-IDEATION-05.md) receipts, quantitative claims, and design folds, performed by Alice in the verification/provenance seat.*

- **verification** (L14) — "All six receipt hashes and every quantitative claim reproduce; the five-item output is **verbatim** from the raw assistant record; all five folds (B1–B5) are present in the design."
- **proposal** (L85) — "I did not edit `MUSE-IDEATION-05.md` (author's file); the fix is proposed."

## ALICE-ORPHAN-EVIDENCE-GUARD-REV2-CHECK.md
*A second-seat verification re-check by Alice confirming that both findings from her earlier review of the orphan-evidence guard rev 2 are closed.*

- **verification** (L13) — "PASS / AGREE — both findings are closed, and the fix is better than the one I proposed."
- **decision_record** (L0) — "Good catch by the owner; my proposal should not be adopted verbatim."
- ~~measurement_report~~ *(was rejected by the strict matcher; the quote is real, emphasis markers differed)* — "Real census: 106 completed, 54 uncited, advisory rc 0, --fail rc 1."

## ANSWER.20260918-162143.md
*This document is a sprint-close status page that synthesizes verdict files to answer research questions about memory systems and retrieval.*

- **synthesis** (L3) — "Written by the planner at sprint close, from the verdict files and roadmap records ONLY."
- **decision_record** (L15) — "Do not build on those justifications; retain the Phase G build restriction."

## ANSWER.20260919-134437.md
*A sprint-close status page written by the planner that consolidates current research answers from verdict files and records build-related decisions.*

- **synthesis** (L3) — "Written by the planner at sprint close, from the verdict files and roadmap records ONLY."
- **decision_record** (L16) — "Retain the Phase G build restriction; the broader adopt/compose/build choice remains unresolved."
- ~~measurement_report~~ *(was rejected by the strict matcher; the quote is real, emphasis markers differed)* — "The tested combination adds no benefit: mean set-F1 stayed at 0.60, with only 1/5 retrieval cases correct and 5/5 abstentions correct."

## CORVID-KEEPWARM-TRIAL-PREREG.md
*This is a pre-registration document defining the measurement protocol for a keep-warm proxy trial on Muse lanes.*

- **protocol** (L7) — "freeze this before the first proxied minute; the metric below is the only pre-specified one."
- **measurement_report** (L25) — "**Baseline (measured 2026-09-14/15):** 14.8–18.3% in the 5–6 min bin; 96.9% in 0–1 min."

## CORVID-S6-3-VERIFY.md
*This document is a verification report by corvid-dsh checking the S6-3 roadmap artifact produced by kiln-flash.*

- **verification** (L10) — "Verdict: VERIFIED PASS with one named minor defect (correction required from the author, non-blocking — the structured data in the same artifact is correct)."
- **measurement_report** (L0) — "The cited arm means "0.600 / 0.500 / 0.250" reproduce to the third decimal."
- **decision_record** (L99) — "so the verdict stands, but the author must append a disclosed correction line to map.md quoting the error — no silent rewrite (D-7 rule)."

## CORVID-S6-3G-VERIFY.md
*This document is a gate verification report for row S6-3G in the CORVID project, in which verifier corvid-dsh independently checked the plumb-fable gate against the kiln-flash artifact and issued a VERIFIED PASS verdict.*

- **verification** (L0) — "I authored neither the gate (plumb-fable) nor the artifact it gates (kiln-flash)."
- **measurement_report** (L0) — "gate mtime 2026-09-17 07:39:40 PDT vs earliest artifact mtime evidence.json 08:38:01"

  uncertain: I could not tell what the broader CORVID project structure or the D-7 defect class taxonomy refers to beyond what is stated in this document.

## CORVID-S8-5-VERIFY.md
*A verification receipt from the CORVID project confirming that row S8-5 passed verification on 2026-09-18.*

- **verification** (L60) — "S8-5 **VERIFIED PASS** — done + verified: corvid-dsh 2026-09-18 08:10 PDT"
- **measurement_report** (L30) — "65 tasks / 824 criteria confirmed; 592 (71.8%) expected-output vs 232 (28.2%) incorrect-behavior, range 3–27, mean 12.7 confirmed"

  uncertain: The broader project structure (what the 'sweep' is, what 'row' means in the tracking system, and the relationship between corvid, kiln-flash, and the queue) is not fully explained in this document.

## EXTERNAL-KNOWLEDGEDRIFT-20260916.md
*This is a candidate discovery card documenting the KnowledgeDrift v1 external benchmark, its structure, relevance to the project's goals, and caveats about its scores.*

- **research_intake** (L0) — "This card records what the benchmark claims and what it would be useful for."
- **proposal** (L71) — "So: **adopt the STRUCTURE, verify any SCORE ourselves.**"
- **synthesis** (L46) — "A lexical baseline beating the memory systems is the same shape as our own 2026-09-16 result (bm25 25/30 against claude-mem and pi-lcm at 0/30 raw, 30/30 and 7/30 corrected)."
- **verification** (L66) — "The numbers also disagree with themselves."

## KILN-D-8-VERIFY.md
*This document is a verification report by kiln-flash checking row D-8 of a backlog against its declared terms and issuing a VERIFIED PASS verdict.*

- **verification** (L0) — "The D-7 extrapolated-stamp class did NOT land in the filed instance; the self-correction is the extrapolation trap being caught by the very discipline D-7 exists to enforce."

## MUSE-IDEATION-01.md
*This document records a batched ideation call to an AI model (Muse) in which nine candidate items were dispositioned into three accepted proposals, five duplicates, and one rejection.*

- **proposal** (L67) — "The three ACCEPTs above are the proposed next probes; Q2.3 folds into the lane-counter design I already own, and Q1.2/Q3.3 are cheap instrument extensions."
- **measurement_report** (L11) — "The whole call cost about a tenth of a cent."
- **protocol** (L64) — "One batched Muse call per R&D item, prompt recorded before the call, all content public/synthetic."
- **decision_record** (L48) — "The designed counter never increments shared state: it reads provider-side balances (`meters.py`) and harness-written per-session `tokenUsage`."

## MUSE-IDEATION-03.md
*This document records a batched ideation call to an AI tool (Muse) asking for additional static-checkable evidence-integrity defect classes, with a disposition table and a decision on which to pursue first.*

- **research_intake** (L12) — "I asked Muse for *other* evidence-index mistakes a simple static checker could catch, because the invalidated-pointer checker I just built covers only one."
- **verification** (L0) — "I judged three new and worth building, two already covered."
- **decision_record** (L0) — "It is the same defect family as the three bad pointers already found, and it is pure static resolution — no schema, no hashes, no new data."
- **proposal** (L30) — "Next bounded step: extend `check_invalidated_pointers.py` to resolve every `results/`/`research/` link and flag dangling targets, with a synthetic dead-link self-test."

## S3-1-STANDARD-TIER-FREEZE-20260915.md
*A sponsor decision record that freezes the standard-tier corpus parameters for the S3-1 assay.*

- **decision_record** (L17) — "The sponsor has now given the decision directly."
- **protocol** (L36) — "S3-1 executes the deterministic, harness-trigger firing run only (no LLM-judged product score, no score import, no cross-system headline below `standard`)."

  uncertain: It is unclear whether 'Corvid' is a person, a system, or a document author within the project.

## S6-SELECTIVITY/design.md
*This is a design document for S6-2, a selectivity diagnostic that defines a frozen corpus, control arms, a Set-F1 scoring metric, and a pre-declared separation-margin decision rule for distinguishing selective retrieval from a firehose baseline.*

- **protocol** (L69) — "Set-F1 of `retrieved_ids` against the manifest's declared helpful set, per case; an abstain case scores 1.0 only on an EMPTY retrieval, else 0.0."
- **research_intake** (L11) — "Its own headline (a lexical baseline above the memory systems) independently reproduces the shape of our S4-14 result."
- **proposal** (L3) — "Row S6-2 (Astra's Sprint-6 proposal, Brian approved 2026-09-16 evening)."

## SCOREBOARD-20260912.md
*A running scoreboard and status log for Sprint 2 of a research project on AI coding agents with memory, tracking measurements, verifications, fleet operations, and open items across multiple agent seats over two working days.*

- **measurement_report** (L15) — "Goal-2 smoke is green post-fix: 36/36 match."
- **verification** (L276) — "Alice checked Corvid's P2 evidence-gate card."
- **operations** (L216) — "The nightly engine switch erased the conversation history of all four "flash" lanes (builder)."
- **synthesis** (L108) — "Task list is now 35 of 36 done."

  uncertain: It is unclear whether this file is the canonical scoreboard or a derived copy, and what the exact relationship is to the referenced team/SPRINT-2-DEMO.md.

## SPARK-OUTCOME-PROTOCOL-ADDITIONS-20260914.md
*A proposal document from muse-drafter (Spark) suggesting three new outcome metrics (M5–M7) for the goal-5 protocol, referencing outside benchmarks for their measurement design.*

- **proposal** (L3) — "Proposal only — no edit to a frozen spec."
- **protocol** (L0) — "if accepted, add to §3 with the same unit/start-stop/detection/anti-gaming discipline and extend §3.1."
- ~~research_intake~~ *(was rejected by the strict matcher; the quote is real, emphasis markers differed)* — "Source: HaluMem **False Memory Resistance** (`N_miss/N_distractors`)."

## SPRINT-4-OUTLINE.md
*This document is a Sprint 4 outline for the corvid-dsh project, proposing three goals, recording an adjudication decision among competing plans, and defining operational bounds for the sprint.*

- **proposal** (L8) — "Fix the one result we have, make "done" mean something, then measure real systems — in that order."
- **decision_record** (L40) — "A compromise doing a bit of all four was the named failure mode; Assay's plan won outright."
- **operations** (L51) — "Free GLM-5.3-Flash via ZCode 08:00–18:00 local only, through 20 Sep; a timer stops the fleet at 18:00, so every goal must be resumable."
- **protocol** (L16) — "Done when: the corrected report exists, states the exact times it ran and the exact frozen list of inputs it read, and the fixed test passes its own checks."

  uncertain: I could not tell what the broader research project is investigating beyond this sprint's memory-related assistant finding.

## VERITY-CITATION-RULE-CHECK.md
*This document is a rule check by Verity of Corvid's citation rule draft Rev 2, giving a PASS verdict with two editorial tightenings.*

- **verification** (L6) — "Verdict: PASS with two tightenings (both editorial, owner Corvid)"

