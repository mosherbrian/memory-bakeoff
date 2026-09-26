# Reading note c71 — claude-mem configuration/progressive-disclosure: what is bounded, what is automatic

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 71.**
Skeleton first; **one primary**: claude-mem's own configuration / progressive-disclosure docs.
No paper rereads, no sweep, no probe. Questions: what is **bounded** (fixed budgets/caps), what is
**automatic versus actor-invoked**, and **evidence versus claim** for each. C70 corrections
carried: ReMe footers = paper-side utility-deletion, not a verified current product; **README
absence is not cap/invalidation absence**; injection could aid application and is **not**
independent command enforcement. Recommendation already exists; unknowns stay non-blocking.

*(facts + verdict appended below)*

## What the docs source actually specifies

**Automatic (hook-driven):** every SessionStart supplies a **compact index** — ID, time, type,
title, **per-item token count** — the docs' worked example: naive priming 35,000 tokens at start
(~6% relevant) versus index of 50 observations ≈800 tokens + fetches ≈120 each → 920 tokens
(100% relevant). **These are constructed illustrations, not measurements** — the ~10× savings is
arithmetic on their own example.

**Bounded:** index tier guideline ~1,000 tokens ("agent has 99,000 free"), per-fetch ≈200 tokens,
costs visible per item. **Not bounded:** total detail retrieval. The docs delegate it explicitly:
*"The agent knows… how much budget to spend, when to stop searching. **We don't.**"* The only
hard numbers documented are operational — hook timeout default 60 s, their own recorded
observation that 60 s was **too short** for npm install, configured 120 s. A capture path that
can time out is a failure mode, and it is documented rather than hidden.

**Actor-invoked:** everything past the index — search, timeline, full fetches. The design stance
is deliberate: judgment stays with the actor; the product makes **costs visible** rather than
enforcing limits. The docs even absorb the c63 lesson: 100K window ≠ 100K useful attention.

## Evidence versus claim, itemized

| claim | status |
|---|---|
| compact index auto-injected at SessionStart | **supplied mechanism** (hooks documented) |
| ~10× token savings, 6%→100% relevance | **illustration**, no method or measurement |
| agent spends budget wisely when fetching | **assumption, explicitly owned** ("we don't know best") |
| delivery/application improves | **no outcome evidence** |

## Verdict — refinement of c70, corrections applied

The injection path is **not identical** to the failing native index: it is a **token-guided,
cost-visible index**, which is the shape the load-cap discussion wanted — bounded first tier,
per-item costs, overage visible. But the docs confirm the boundary: **automatic ends at the
index; authority and application remain actor judgment, by design.** Injection could aid
application (a lesson in a 1K index is harder to plead unseen than one truncated away); it
enforces nothing and adjudicates nothing. ReMe contrast restated correctly: paper-side
utility-deletion, not a verified product feature on either side.

**Bounded recommendation unchanged, unknowns non-blocking:** comparator for the delivery tier's
*shape* (bounded cost-visible index), not evidence of outcomes; enforcement pilot ordering
unaffected. **Confidence: high on automatic-vs-actor split (docs explicit), high that budget
figures are illustrative (their own framing), medium that the index shape transfers to Brian's
109/301 problem without host changes.**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, COVERAGE.md.

### Tern closeout qualification

Illustrative token budgets and per-item costs do not establish a hard first-tier bound or user-visible overage. Source-read v13.27.1 instead supplies a 10k-character reduction target with a residual-overage path, as reconciled in [cycle71 response](../panel-response-c71.md). Hook execution timeout and context-output size are separate limits; an installation timeout example is not evidence of capture loss. No change to the enforcement-first recommendation or optional Letta pilot.
