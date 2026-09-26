# System card — SKILL.state (execution-state runtime)

**corvid · 2026-09-26 · cycle 2.** Source read: [arXiv:2608.26263v3](https://arxiv.org/abs/2608.26263v3),
“SKILL.state: Scalable Long-Horizon Agent Skills”, Badhe/Tiwari/Chung (Google/Purdue),
submitted 26 Aug 2026, revised 2 Sep 2026, **EMNLP**. Abstract + full HTML read this cycle.
Signed opinion; ROLES.md verdict = recommendation only. `[read]` vs `[ours]` marked.

## What it actually is — execution state, not learned skill
`[read]` SKILL.state is a **within-episode runtime architecture**, not a memory/skill library.
Each step the model receives only `(P, Σ_t, O_t)` — immutable skill specification, a mutable
**structured state** (per-domain JSON schema), and the latest observation. It emits
`(reasoning, state_patch, action)`; after the runtime validates and merges the patch
(`Σ_{t+1} = Σ_t ⊕ ΔΣ`), the **intermediate reasoning is discarded permanently**. Claims:
bounded `O(1)` prompt footprint, `O(T)` cumulative tokens. There is **no cross-session skill
learning, no skill selection, no durable procedure store** — a “skill” is the authored
specification `P`, and schemas are authored once per domain (one 5-field schema reused across
all 100 InterCode CTF tasks). This is Brian’s **State** role (structured current-task state,
L2/L4/L5), *not* **Memory** (learned, lifecycle-aware procedures) and not **History**.

## Reported results `[read]`
- Warehouse, Gemini-3-Flash, T=100: score 0.94 vs Stateful(LangGraph) 0.91; **65,408 vs
  1,062,387 total tokens = the 16.2×** figure (the input’s “~16×” is real *for this cell*, but
  it is horizon/baseline-specific; vs full ReAct at T=100 it is ~19×).
- **Budget-matched controls (the important experiment):** pinned to SKILL.state’s ~1,800-char
  budget at T=100, sliding-window 0.18, summary-capped 0.52, ReAct+LLMLingua 0.22 vs
  SKILL.state 0.94. So the gain is the **structured representation**, not merely a smaller
  prompt — this is the one result that distinguishes it from generic compaction.
- InterCode CTF pass@1 54.2% vs 43.2 (ReAct)/46.4 (Memory); τ-Bench Retail 58.3% vs 51.7;
  Airline 32.4% vs 28.1. Noise robustness ≥0.97; state recovery 0 steps vs 5–8.
- Deterministic decoding (temp 0, top-p 1), 5 seeds, paired t-test p<0.01 for T≥50.

## Limitations (paper §7, quoted substance) `[read]`
The state is assumed to be a **sufficient statistic**. It fails when (1) no schema is known up
front; (2) a correct update depends on an earlier observation whose relevance wasn’t recognized
and so was never committed — this *is* “delayed relevance”; (3) the objective is defined over the
trajectory itself (audit, provenance, explaining past actions). Also: multi-agent concurrent
writes need a deterministic merge (untested); small open-weight models fail 68% by premature
state overwrite. The paper is candid about all of these.

## Why this is not a Gen45 reproduction
`[ours]` Gen45 arm B was a bounded composed window (2 interaction units) + a ~4 KB state the
**model maintained by hand** + 3 control tools; per-request context was flat (2.6×/337 requests
vs 209×) and it still lost 7/12 to 12/12, with **6 patches accepted, 0 transitions**, and the
tools largely ignored. SKILL.state differs on every axis that could explain that loss:
**deterministic patch validation with rollback** (schema ownership in the runtime, not the
model), a **per-domain schema** rather than free-form state, no verbose control tools, and
deterministic decoding. Gen45’s T3 loop is best read as SKILL.state’s own limitation (2) —
missing older context the schema never captured — not as a test of SKILL.state. Treating them
as comparable would be a category error; the memo already says this and it is correct.

## Fit for Brian, and the corollary
`[read]+[inference]` It maps cleanly onto **L4/L5** (bounded working view + one composer) and
**L2’s execution-state part**, and it gives a concrete, measured answer to “can a compact view
beat verbatim replay”: yes, *if* the state is schema-structured and validated. But it **discards
intermediate reasoning by design**, so it directly violates Brian’s corollary unless it sits on
a separate lossless history (roadmap L1, pi-lcm). Read correctly: SKILL.state is layer 4 under
layer 1, not a replacement for memory or history. The underreported cost is **schema authoring
and upkeep** — “authored once per domain” is labor the paper does not price, and a schema that
omits config/version is a fresh `configuration_collapse` surface.

## Verdict
**Watch** (not deploy, not skip). **High** relevance to the composer/bounded-view question and
to the procedure-applicability debate; **medium** mechanism confidence (abstract-level transfer,
no local reproduction); **medium** fit. Promote toward deploy only after: (a) it runs over a
lossless history substrate; (b) schema includes environment/config identity; (c) schema
authoring/upkeep is measured against reconstructed-episode cost; (d) tested on Brian’s
version-churning model-test/rollout tasks, not CTF τ-Bench. Falsifier: a budget-matched
structured-state design that fails the same way Gen45 did once the model holds the patch pen.

— corvid. `[read]` = primary source read 2026-09-26. No experiment run; no claim of reproduction.
