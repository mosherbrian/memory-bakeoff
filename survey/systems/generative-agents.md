# System card: Generative Agents (reflection/plan machinery, borrowable parts)

**kiln · 2026-09-26 · sources: paper methods arXiv:2304.03442v2 §§1–4.3, 6 (read this session) + author repo joonspk-research/generative_agents (README + layout, read-only clone, nothing executed). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## How observations/reflections/plans persist

- **Memory stream:** comprehensive NL observations, each with creation + last-access timestamps. Retrieval scores recency (exp decay 0.995 over game hours) + importance (LLM 1–10 assigned at creation) + relevance (embedding cosine to a query), equal weights, top-k into context. Everything persists — but note the qualification: "comprehensive" means everything *the sandbox engine emits*, a bounded event firehose, not open-ended experience. All-observations-persist does not transfer to Brian's unbounded world.
- **Reflections:** second memory type, higher-level, generated when importance-sum of latest events exceeds 150 (~2–3×/day), recursively synthesized into trees; reflections re-enter the stream and retrieve alongside observations. Evidence support: reflections are generated *from retrieved observations* in the reflection prompt — but exact-quote citation discipline was not verified in my read (marked).
- **Plans:** day plans from observations + reflections, recursively decomposed; new observations trigger react/re-plan; dialogue updates plans. Plans also re-enter the stream.

## Re-planning triggers and evaluation reality

Re-plan fires on contradicting/interrupting observations and dialogue — reactive, not scheduled. Evaluation measures human-rated *believability* (interviews + emergent social behavior), with ablations showing each component contributes; documented failure modes: retrieval misses, fabricated embellishments, inherited formal speech. Believability ≠ dependable assistance — the paper optimizes the former and reports the latter's failure modes honestly.

## Borrowable without the simulated world

Importance-at-write scoring, importance-sum reflection trigger, weighted-combination retrieval, reflections-as-memory, plan-from-reflections with re-plan on contradiction — all portable as file conventions + closeout discipline. What stays behind: the bounded observation firehose, per-agent stream, game loop, and the evaluation (no believability judge exists for Brian's admin work).

## Prototype vs maintained plug-in

The repo is a 2023 research prototype (reverie backend + Phaser frontend, OpenAI-key setup, last commit years old as observed) — prototype, unambiguously. Install cost for Brian's purposes is not the point; nothing here ships as maintained tooling. No installation performed.

## Verdict: **borrow three mechanics, skip the system**

Importance scoring, reflection trigger, re-plan-on-contradiction port to native files at ~zero cost; the system (sim + believability apparatus) has no Brian-shaped deployment. **Medium-low confidence** (methods read; transfer argued, evaluation mismatch explicit).
