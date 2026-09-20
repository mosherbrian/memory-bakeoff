# muse-drafter: fixed-by-construction supersession probe (StateMemBench transfer; spark pulse 2026-09-14)

Follows `CANDIDATE-CARD-STATEMEMBENCH.md` Next-step 2 ("adapt the fixed-by-construction supersession probe to our case-authoring guide"). Design only, no run. Companion to SPARK-STALE-PATH-PROBE-SKETCH (that one transfers LME-V2's gotcha/premise items; this one transfers StateMemBench's generator discipline). For P1 case authors to accept/reject.

## Source discipline (StateMemBench, from the card)
Scenarios generated as symbolic event programs (typed state ops over ground/derived/declared state); gold by deterministic replay; traps placed exactly where lazy-reader policies (recency / frequency / stale-derivation / eager-invalidation) disagree with replay → failure-mode signature fixed by construction. Probes closed-pool (gold + drift target + neutral distractors) so drift vs off-pool is separable.

## Transferred discipline for our P1 cases
1. **Write the program first:** each new P1/P1-2/P1-3 case gets a 5–10-line event program (DECLARE value → SUPERSEDE value → DERIVE dependent → QUERY) before any dialogue is authored. Gold = replay output, not author judgment.
2. **Place one trap per lazy policy:** for each case, mark which of the four lazy readers would fail it (recency: new value buried under chatter; frequency: old value repeated more often; stale-derivation: dependent computed from pre-update value; eager-invalidation: unrelated value wrongly retired). One case, one primary trap — the case's failure-mode label is fixed at authoring time.
3. **Closed-pool probes:** every supersession query ships gold + drift target (the superseded value) + 1–2 neutral distractors drawn from live state. Score: current / drift / other. Drift-vs-other separation is what makes a stale-use claim citable instead of anecdotal.
4. **Cost control:** the program is a few lines in the case file, not a harness — zero infra, applies to hand-built cases immediately.

## Non-overlap with the stale-path sketch
Stale-path sketch = *what to ask* (3 probe questions per decommissioned path). This note = *how to author* (program-first gold + one-trap-per-case + closed pools). Adopt independently; combined they make a case whose gold, trap, and probes are all fixed before data exists (cf. DESIGN-CORNERS Corner 7b: disclosures pinned before data).

$0, design sketch, no Muse batching. — muse-drafter (Spark)
