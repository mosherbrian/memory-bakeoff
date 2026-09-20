# ASTRA SPRINT-5 REVIEW — publish call, Sprint 6 scope, roadmap coverage

**Author:** gpt-6-astra via `codex exec`, commissioned by Brian 2026-09-16.
**Inputs:** the S4-14 re-run summary, RETRO-4-SUMMARY.md, PHASE2_ROADMAP.md,
the approved portfolio charter header, and MISSION-20260912.md — the documents
themselves, not a summary of them. **Asked to argue with** Claude's publish
recommendation rather than agree with it.

**Two findings verified against the source before filing:**
1. The arithmetic discrepancy in F4 is REAL. The table reports 19/60 scenarios
   with at least one non-empty turn, which leaves 41 with none — F4 says 37.
2. The fixtures are future-dated relative to the evaluation clock: records
   stamped 2026-09-01, `eval_now` pinned 2026-08-30. Unexplained.

---

**Publish a corrected methods note; do not publish an engine ranking.** I agree with Claude’s central objection, but “measured properly for the first time” still overstates what was established. These are corrected retrieval paths on a narrow test, including a declared pi-lcm adaptation and a shared-LSA implementation of claude-mem’s search policy. They are not complete product evaluations.

**Brian’s decision:** authorize a correction that replaces the earlier interpretation of the zeros, and withhold comparative product claims.

The publishable finding is useful: changing the retrieval configuration changed the measured result dramatically without changing the corpus or trigger. The old zeros were real outputs from unsuitable configurations. Verifying the arithmetic did not validate the experiment.

Claude is right that the current test cannot establish retrieval selectivity. With only one stored record, returning everything guarantees that record appears. Claude-mem’s 30/30 therefore demonstrates coverage, accompanied by every near-miss firing; it does not demonstrate that the system can choose useful memories from competing ones. Also, 30/119 is **trigger FirePrecision**, not retrieval precision. Those should not be presented interchangeably.

Pi-lcm’s 7/30 versus BM25’s 25/30 is a valid description of these configured paths on this instrument. It does not establish a product ranking. Likewise, zero FalseFire deserves little reassurance when all arms achieve it while NearMissFire varies substantially.

Before publication, fix two visible inconsistencies:

- Nineteen of sixty scenarios have a nonempty retrieval turn, leaving **41**, not the **37** stated in F4. Establish which count or description is wrong.
- The records are dated September 1, while the evaluation clock is August 30. Explain the future-dated fixtures and exactly what temporal behavior was tested. Matching window-on/off results supports “no observed window effect here,” not general temporal correctness.

**A ranking becomes publishable when a frozen test makes indiscriminate retrieval lose, and a claimed ordering survives credible comparison.** Concretely:

- Use multiple records per store: relevant evidence, plausible distractors, and cases where nothing should be retrieved.
- Declare which records would help before running engines. Include scoped or outdated records where relevance depends on the question.
- Compare against BM25, return-nothing, and return-everything under a declared, comparable context budget. The existing always-fire control tests the trigger; it does not replace a return-everything retrieval control.
- Report useful retrieval, irrelevant material admitted, trigger behavior, and cost separately. Check whether conclusions hold across scenario families and account for uncertainty.
- Freeze adapters after unrelated ingestion/search checks and primary-source review. Label product paths, approximations, and adaptations precisely.

That could justify a **ranking of specified configurations on the new benchmark**. A claim about making agents better at work additionally needs G4 task outcomes.

**For Sprint 6, I recommend exactly two rows.** Brian would approve these two deliverables and keep execution within the existing spend limit and September 20 promotional deadline.

1. **Make the invocation test capable of rejecting indiscriminate retrieval.** Advances **G3 invocation** and roadmap **Phase D’s admission discipline**, with preparation for **Phase H’s scope and context-budget questions**.

   Kiln builds and runs a small, frozen, multi-record diagnostic using the current scenarios where practical. Include distractors and no-relevant-memory cases; run the three controls first. If return-everything remains indistinguishable from selective retrieval, stop and report that failure rather than spending on engine comparisons. If the instrument separates them, run the corrected paths with explicit implementation labels.

   Corvid reviews the frozen cases and adapter assumptions before scored runs, then independently checks the results afterward. Cairn schedules and checks completion evidence. Worker turns are serialized; a long local test still reserves the shared request slot until that turn ends. Completion means a reviewed diagnostic and an explicit conclusion about what it can distinguish—not a guaranteed ranking.

2. **Restore the roadmap as the execution authority.** Advances roadmap **durability rules 4–7**, **Decision Gate F**, and the charter’s required reconciliation.

   Produce one compact evidence map: roadmap commitment, supporting artifact, current status, and next decision. Reconcile the stale charter with the three-seat roster, single-request constraint, and expiring free window. End with one proposed experiment connecting the strongest supported architecture question to **G4 material outcome**, including its baseline and stopping rule. This row proposes that experiment; it does not build the composite.

   Cairn assembles the map, kiln checks implementation claims, and corvid checks evidence independently, in sequence.

**Brian’s remaining operational decision:** before September 20, set the post-promotion resource envelope. Until then, Sprint 6 should leave no run dependent on promotional access continuing afterward. Neither worker needs simultaneous API work.

**Against the roadmap, the recent work shows real progress but incomplete strategic coverage.** The brief does not contain every artifact from all four sprints, so “not evidenced here” must remain distinct from “never done.”

- **Phase D—admission:** hashes, frozen harnesses, deterministic checks, and declared adaptations advanced it. Source-path validation failed before S4-12 and was repaired afterward. Cheapest next step: require each remeasurement row to link its prior result and validated product path before execution.
- **Phases B/C—field refresh and mechanism-based selection:** the ecosystem map and claude-mem revisit show some progress. A current intake/rejection ledger and a small batch selected by distinct architectural questions are not evidenced. Cheapest next step: recover existing decisions into the evidence map before commissioning another field survey.
- **Phase E—external lanes:** the conflict benchmark anchors advance this. Keeping their scores separate from invocation scores follows the roadmap correctly. Broader named lanes are not evidenced; they should remain explicitly deferred, not automatically become new work.
- **Phase F—architecture synthesis:** no current architecture matrix or explicit adopt/compose/build/reproduce decision is supplied. This is the most consequential missing bridge. Populate it from existing evidence and identify one uncertainty that would change the decision.
- **Phases G/H—composite and realism:** invocation work is preparation, not evidence of a working composite or improved sustained task performance. Do not declare these phases completed—or prematurely build the composite. Preregister the smallest material-outcome comparison once Phase F identifies the intervention.
- **Durability:** recovering and linking the roadmap repaired access. Its repeated omission from sprint goals shows that access alone did not make it govern work. Require every row to cite a goal or roadmap item, as Brian now requests.

**The team’s own failure is worth publishing as a documented incident, not yet as a general experimental result.** It has an unusually clear chain: relevant knowledge existed, was not consulted, an unsuitable configuration was certified, and consulting that knowledge changed the result.

The stronger research question is whether routing prior evidence into decisions prevents repeats without excessive reading or delay. One retrospective incident cannot prove that. **Brian’s decision:** allow a short case study alongside the correction; reserve any claim of a memory breakthrough for a prospective comparison that changes agent behavior.
