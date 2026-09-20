# Council advice — stratum-glm

**Recommendation:** Sprint 7's one goal: make the invocation instrument able to fail a firehose, then freeze it — advances **G3 invocation** and roadmap **Phase D** (admission discipline). Everything else waits.

Sprint 6 already spends its three rows on the correction (S6-1), the diagnostic (S6-2), and the evidence map (S6-3). The next sprint must not open new fronts until S6-2's diagnostic answers its yes/no question. If the diagnostic separates selective retrieval from return-everything, Sprint 7 runs the corrected engine paths on it and reports a real comparison. If it cannot, Sprint 7 reports that failure and stops engine comparisons rather than spending on numbers that prove nothing. One goal, decided by S6-2's outcome — this is what keeps the project from drifting while each sprint looks sensible.

## Rows

**Row 1 — Run the frozen diagnostic against corrected paths (kiln does, corvid reviews).**
Deliverable: scored diagnostic run on the S6-2 frozen multi-record instrument (distractors + no-relevant-memory cases + return-everything control) with pi-lcm tool-level, claude-mem chroma no-recency, BM25, return-nothing, and return-everything arms.
Artifact: `team/S7-DIAGNOSTIC-RUN.md` + results dir beside it.
Check: return-everything arm scores measurably worse than selective retrieval on the pre-registered penalty (precision/irrelevant-admitted cost), and return-nothing scores worst on coverage — if either check fails, the row closes as "instrument cannot separate; no engine comparison published," which is itself the deliverable. Re-measurement rule: cite S4-14 and S6-2 priors in writing.

**Row 2 — Publish the correction note with the two arithmetic fixes (corvid drafts, cairn assembles).**
Deliverable: a stranger-readable correction replacing the S4-12 zeros interpretation, with F4's 19/60-vs-37 count fixed and the future-dated fixtures (records 2026-09-01 vs eval_now 2026-08-30) explained, carrying Astra's coverage-not-selectivity caveat.
Artifact: `team/S7-CORRECTION-NOTE.md`.
Check: a second seat verifies both fixed numbers against the run logs and signs; no engine ranking language survives (grep for "beats/ranking/best" returns nothing outside the caveat).

**Row 3 (only if Row 1's instrument separates) — Phase F architecture matrix, first pass (cairn assembles, kiln checks implementation claims, corvid checks evidence).**
Deliverable: one-page matrix per roadmap Phase F columns populated strictly from existing measured evidence, ending in one proposed G4 material-outcome experiment with baseline and stopping rule.
Artifact: `team/S7-EVIDENCE-MAP.md`.
Check: every cell cites an artifact path or says "no evidence"; any uncited cell fails the check. If Row 1 fails, this row does not start — two rows is a complete sprint.

## What I would NOT do

I would not build the composite (Phase G), run new external benchmark lanes (Phase E breadth), or admit any new engine or ablation. Three reasons: (1) with a one-record store the instrument cannot distinguish coverage from selectivity, so every new engine number is uninterpretable — more arms multiply the appearance of progress while the measuring stick is broken; (2) the one-request-in-flight contract plus the 09-20 free-window expiry means serialized, budget-inside-Go work only — breadth spending now risks runs stranded mid-matrix when promotional access lapses; (3) Phase F's adopt/compose/build decision is unmade, so building the composite today is construction before the blueprint. The plausible thing I am refusing is "while we wait, measure three more systems" — that is exactly how S4-12 happened.

I would also not publish any ranking, product claim, or the incident write-up as a research result — Brian already ruled on all three, and relitigating them spends the sprint's scarcest resource (his attention) for zero evidence gain.

## What I am most likely wrong about

That the multi-record diagnostic will actually separate firehose from selective retrieval on this scenario family. If near-miss and distractor design is weak, return-everything may still tie or win on FirePrecision-style trigger metrics, and we will have spent the sprint learning the instrument needs a redesign rather than getting a ranking. I accept that trade: a frozen "cannot separate" verdict is worth more than another 30/30 that means nothing. Second candidate: my assumed serialization (kiln runs, corvid reviews, never concurrent API) may be over-cautious after 09-20 if the Go plan lifts the concurrency cap — verify before designing around it, per the queue header.
