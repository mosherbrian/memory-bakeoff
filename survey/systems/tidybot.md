# System card: TidyBot (examples → summary → grounded action)

**kiln · 2026-09-26 · sources: paper full methods 2305.05658v2 (§§1–4, 6, limitations) + author repo jimmyyhwu/tidybot (benchmark/ per-method notebooks + scenarios.yml, server/ camera/controller/detector + preferences/*.yml; read-only clone, nothing executed). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Capture, persistence, rule use, grounding, action

- **Example capture:** 4–10 textual placements per user per scenario; benchmark scenarios in scenarios.yml; server preferences/*.yml per scenario.
- **Summary persistence:** the LLM summary text *is* the artifact — regenerated per user, not versioned, not accumulated across sessions. No long-term store, no cross-user learning.
- **Rule use:** summary → unseen-object placements + noun extraction → CLIP category set → per-object receptacle/primitive selection in an until-floor-clear loop.
- **Perceptual grounding:** ViLD localization (92.5%), CLIP over summary categories (95.5% vs 52–71% with human object lists — the summary *shrinks* the label space, a genuine mechanism), hard-coded receptacle positions, ArUco pose.
- **Action:** pick/place/toss primitives (96.2% execution); 85.0% end-to-end real-world, 91.2% benchmark unseen.

## Correction path: described vs missing

Described: re-teach with corrected examples → re-summarize (fresh summary supersedes by replacement). Missing: versioning of summaries, audit of which summary acted, revision short of full re-teach, recovery of a superseded-but-correct rule. Limitations (§4.6) admit imperfect summaries; human summaries gain +6pts — the extraction quality ceiling is measured, not wished away.

## Software-host transfer (pattern, not robot)

The loop ports directly: user examples → summarized preference rule → category set → per-item classify → act, with the summary shrinking the decision space (the CLIP-label-space result generalizes: good summaries reduce classifier load). Robot primitives stay behind; software analogues (search, test, file ops) slot in. What transfers is small and honest: few-shot preference capture with a human-readable summary artifact, plus the measured warning that summary quality caps everything downstream.

## Facility assessment

Research robot facility + benchmark harness, not a deployable memory operation: per-session recompute, no persistence layer, no host adapter, no correction API. **Borrow the capture-then-summarize shape; skip the system. Medium-low confidence** (methods + repo read; numbers fenced to their settings).
