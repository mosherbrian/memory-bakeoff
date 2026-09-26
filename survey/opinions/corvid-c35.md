# Contrarian, cycle 35 — reflection should propose, not authorize

**corvid · 2026-09-26 · cycle 35.** Signed opinion; ROLES.md “best rival idea.” Source: Generative
Agents, Park et al., UIST 2023 (2304.03442v2), methods/controls. `[read]` Confidence **medium**.

**Strongest positive case.** Generative Agents pairs a **memory stream** (timestamped observations
with importance) with retrieval by **recency × importance × relevance**, periodic **reflection**
that synthesizes higher-level insights from recent observations (and stores them back with
evidence), and **recursive planning** with re-planning on new observations. The point our modest
guidance store misses: reflection **generates initiative** — patterns and plans the agent was
never told, e.g. proposing a next action from accumulated experience. A store of authored/
promoted guidance cannot produce that; it only retrieves what someone already wrote. So there is a
real capability gap on the *proposal* side, and reflection is the mechanism that closes it.

**But believability ≠ dependable assistance.** The paper’s headline evidence is **human-rated
believability and coherence** under controlled ablations (removing reflection/re-planning degrades
rated behavior) plus an end-to-end simulated town — not task success, and not transfer to Brian’s
admin/rollout work. A believable, coherent plan can still be wrong or unsafe.

**Practical recommendation.** Add a **reflection pass that emits candidate insights/plans with
evidence pointers**, feeding the guidance store as **candidates** (c27/c28) — never authority, never
auto-binding. It supplies initiative while sponsor directions and artifacts keep deciding what
binds. **Reversal:** if reflection yields plausible-but-wrong initiatives that propagate
(experience-following), or its value cannot be tied to outcomes rather than to raters finding it
coherent, restrict it to non-binding suggestions or drop it.

— corvid. No experiment.
