# Stage-one review set, repaired instructions - 2026-09-19

20 documents, all 20 this time. Zero rejected quotes, zero errors. Every quote is verified present in its file; what needs your read is whether each ROLE is right for the sentence supporting it.

Three files were sent head-and-tail and are marked PARTIAL INPUT: a role absent there may simply not have been shown.

## ALICE-MUSE-BATCH5-SECONDCHECK.md
*A second-seat verification check on a Muse batch 5 ideation artifact and its receipts, performed by Alice in the verification/provenance seat.*

- **verification** (L14) — "All six receipt hashes and every quantitative claim reproduce; the five-item output is **verbatim** from the raw assistant record; all five folds (B1–B5) are present in the design."
- **proposal** (L85) — "I did not edit `MUSE-IDEATION-05.md` (author's file); the fix is proposed."

## ALICE-ORPHAN-EVIDENCE-GUARD-REV2-CHECK.md
*A second-seat re-check document verifying that rev 2 of an orphan-evidence guard script addresses two findings from rev 1.*

- **verification** (L13) — "PASS / AGREE — both findings are closed, and the fix is better than the one I proposed."
- **measurement_report** (L53) — "Synthetic trees under `/tmp` plus a read-only real census; no tree modified."

## ANSWER.20260918-162143.md
*A research status page written at sprint close that synthesizes current answers to six research questions from multiple verdict files and notes what is decision-ready.*

- **synthesis** (L3) — "Written by the planner at sprint close, from the verdict files and roadmap records ONLY."
- **decision_record** (L15) — "Do not build on those justifications; retain the Phase G build restriction."

  uncertain: What Gate F and Phase G specifically refer to, and what the broader adopt/compose/build choice entails, is not explained in this document.

## ANSWER.20260919-134437.md
*A sprint-close status page that synthesizes multiple verdict files into current answers for research questions and records decisions about which build justifications to reject.*

- **synthesis** (L3) — "Written by the planner at sprint close, from the verdict files and roadmap records ONLY."
- **decision_record** (L16) — "Reject the tested composition and state-layer justifications for building: the combination adds no retrieval benefit, and the layer fixes no observed native supersession failure"

  uncertain: No project name is stated in the document; the sprint and phase labels (Phase G, sprint close) are referenced but the enclosing project is not named.

## CORVID-KEEPWARM-TRIAL-PREREG.md
*A pre-registration document specifying the metric, pre-specified checks, and decision rule for a keep-warm proxy trial on Muse lanes.*

- **protocol** (L7) — "freeze this before the first proxied minute; the metric below is the only pre-specified one."

## CORVID-S6-3-VERIFY.md
*A verification document in which corvid-dsh checks artifact row S6-3 against its cited sources and records a verdict of VERIFIED PASS with one named minor defect.*

- **verification** (L105) — "I verified the artifact against the sources it cites; I did not re-adjudicate whether the roadmap's commitments are the RIGHT commitments."
- **decision_record** (L10) — "Verdict: VERIFIED PASS with one named minor defect (correction required from the author, non-blocking — the structured data in the same artifact is correct)."

## CORVID-S6-3G-VERIFY.md
*A gate verification report for row S6-3G, authored by corvid-dsh on 2026-09-17, confirming that the plumb-fable gate correctly enforces the distinctions required by the row.*

- **verification** (L86) — "Row S6-3G: artifact exists, declared check exits 0, independence structural, gate rejects distinction-less and falsified documents by name. VERIFIED PASS."
- **measurement_report** (L64) — "a commitment's status collapsed to "missing" → REJECTED (`STATUS-COLLAPSED`)."

## CORVID-S8-5-VERIFY.md
*A verification receipt recording that row S8-5 was verified as PASS by corvid-dsh on 2026-09-18, checking the artifact team/S8-HANDBOOK-PASS.md against its cited sources.*

- **verification** (L12) — "Substance, verified 2026-09-18 08:05–08:15 PDT against the row's three requirements"
- **decision_record** (L60) — "S8-5 **VERIFIED PASS** — done + verified: corvid-dsh 2026-09-18 08:10 PDT"

  uncertain: The broader sweep or project this verification belongs to is not named beyond the row identifiers and file paths.

## EXTERNAL-KNOWLEDGEDRIFT-20260916.md
*A candidate discovery card for the external KnowledgeDrift v1 benchmark, recording its structure, its relevance to the project's goals, and proposed next steps for incorporating it.*

- **research_intake** (L0) — "This card records what the benchmark claims and what it would be useful for."
- **proposal** (L78) — "S6-2 must cite this before building its corpus"

  uncertain: It is unclear whether the three options listed for S6-2 (reusing, running against, or building its own) were ultimately selected or remain open.

## KILN-D-8-VERIFY.md
*This document is a verification report for row D-8 of a backlog, checking it against its four declared terms and recording the outcome.*

- **verification** (L66) — "every spot-checked prior citation is real and accurately transcribed"

## MUSE-IDEATION-01.md
*This document records an ideation batch in which Corvid used Muse to generate nine candidate hypotheses and edge cases, then dispositioned each with a verdict (ACCEPT, REJECT, or DUPLICATE) and a reason.*

- **decision_record** (L65) — "Every item dispositioned ACCEPT / REJECT / DUPLICATE with a reason; only ACCEPTs become proposed backlog rows, and only after a run do they become findings."
- **proposal** (L67) — "The three ACCEPTs above are the proposed next probes; Q2.3 folds into the lane-counter design I already own, and Q1.2/Q3.3 are cheap instrument extensions."
- **measurement_report** (L26) — "Latency | 10.46 s (≈3 s pre-first-word, as expected)"

## MUSE-IDEATION-03.md
*This document is an ideation batch in which the author asked an AI system called Muse to name static-checkable evidence-integrity defect classes and then dispositioned each suggestion as accept, duplicate, or reject.*

- **proposal** (L48) — "Muse is divergence, not truth: every ACCEPT becomes a *proposed check*, and becomes a finding only after it rejects a real bad input through its own self-test."
- **decision_record** (L36) — "**Tally:** 3 ACCEPT · 2 DUPLICATE · 0 REJECT."

## QUEUE.md  *[PARTIAL INPUT: partial 40055/456477 chars]*
*A pull-based task queue file for the memory-bake-off project that defines claim protocols, standing rules, recorded decisions, and active sprint rows for a multi-seat research fleet.*

- **protocol** (L3) — "Claim protocol: edit this file to add `claimed: <yourname> <time>` to a row (first writer wins; GiLMore adjudicates collisions)."
- **decision_record** (L73) — "PUBLISH THE CORRECTION, NOT A RANKING. Approved."
- **operations** (L18) — "WIP limit: one row per seat."
- **proposal** (L56) — "Decision, pre-committed: DO NOT BUILD YET."

## RD-THREADS.md  *[PARTIAL INPUT: partial 40055/749714 chars]*
*This document is a standing R&D pool that assigns work threads to named seats and maintains a log of artifacts delivered by those seats.*

- **protocol** (L3) — "Idle = R&D mode. Pick your seat's thread (or self-originate one in-domain), work it one turn, deliver a small artifact (note / test result / finding) into this file's log or team/."
- **operations** (L5) — "Metered seats: your cap is ~$0.05-1 per probe."

## S3-1-STANDARD-TIER-FREEZE-20260915.md
*This document records the sponsor's decision to freeze the standard-tier parameters for S3-1 and lists the frozen values accepted unchanged from Corvid's proposed defaults.*

- **decision_record** (L17) — "The sponsor has now given the decision directly. This file records the override and the frozen values so the tier is no longer unfrozen"
- **protocol** (L36) — "S3-1 executes the deterministic, harness-trigger firing run only (no LLM-judged product score, no score import, no cross-system headline below `standard`)."

  uncertain: It is not clear from this document whether the frozen values were subsequently executed or later amended.

## S6-SELECTIVITY/design.md
*This document is a frozen design for a selectivity diagnostic (S6-2) that pre-declares arms, scoring, and a decision rule for testing whether selective retrieval separates from a return-everything baseline on a 10-case synthetic corpus.*

- **protocol** (L4) — "Design frozen before any run; the manifest pins this design's declarations and the results bind to the manifest by hash."

## SCOREBOARD-20260912.md  *[PARTIAL INPUT: partial 40055/1006334 chars]*
*A sprint scoreboard document (SCOREBOARD-20260912.md) that tracks the evolving status of Sprint 2 work across multiple seats, aggregating progress, decisions, verifications, and open items in time-stamped sections.*

- **synthesis** (L10) — "the newest section is current. Older "Earlier" items are history; an item whose state has changed carries a tag — **[superseded]** or **[resolved]** (Stratum cold read pass 3)."
- **operations** (L216) — "The nightly engine switch erased the conversation history of all four "flash" lanes (builder)."
- **decision_record** (L104) — "Your three decisions from this morning are on file (GiLMore ~08:1x): server.py freeze holds until Cairn's branch lands; meters.py top-up fix approved (builder go); the ~$0.20 DeepSeek charge was yours — new rule is DeepS"
- **verification** (L124) — "I checked: the file fingerprint matches, the 47 extension tests pass, and the commit is on the pushed branch."

## SPARK-OUTCOME-PROTOCOL-ADDITIONS-20260914.md
*A proposal from muse-drafter (Spark) naming three outcome-metric additions (M5, M6, M7) identified from the goal-5 harvest that the frozen SPEC-OUTCOME-PROTOCOL.md §3 does not capture.*

- **proposal** (L3) — "Proposal only — no edit to a frozen spec."
- **synthesis** (L6) — "$0, synthesis of body passes; no score import."

## SPRINT-4-OUTLINE.md
*A sprint outline for Sprint 4, written by corvid-dsh acting as PO on 2026-09-16, proposing three goals, recording a plan selection among four candidates, and setting operational bounds.*

- **proposal** (L8) — "Fix the one result we have, make "done" mean something, then measure real systems — in that order."
- **decision_record** (L34) — "Chosen: **Assay's plan.**"
- **operations** (L50) — "Three seats only. One request in flight fleet-wide (Z.ai Lite contract); a turn is 6–12 s and sends queue behind each other."

  uncertain: It is not clear whether this outline was accepted as written or modified before becoming operative.

## VERITY-CITATION-RULE-CHECK.md
*A rule check by Verity on a citation rule draft (Rev 2), delivering a pass verdict with two proposed editorial tightenings.*

- **verification** (L0) — "Fields 1–6 are all falsifiable by a second seat (pin resolves or it doesn't; operator/​split/​metric/​judge are quoted strings; repro status is a command or `not shipped`; class is a closed vocabulary)."
- **decision_record** (L6) — "Verdict: PASS with two tightenings (both editorial, owner Corvid)"
- **proposal** (L0) — "Tightening T1: require the grade line to name WHO authored it + date (else a later reader cannot weight it)."

