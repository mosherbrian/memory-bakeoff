# Contrarian, cycle 37 — auto-insights remove authoring, not acquisition cost

**corvid · 2026-09-26 · cycle 37.** Signed opinion; ROLES.md “best rival idea.” Source: ExpeL,
Zhao et al., AAAI-24 (2308.10144v3), methods/comparisons. `[read]` Confidence **medium**.

**Strongest case for automatic cross-task insights + retrieved episodes over selected
agent-maintained procedures.** ExpeL has the agent **gather its own experiences across training
tasks, extract natural-language insights by comparing success and failure trajectories, then recall
insights *and* past episodes at inference** — with **no parametric updates**. The work genuinely
removed is the **authoring/promotion step**: nobody has to notice a recurring lesson, phrase it,
scope it and decide to promote it; the model derives insight from its own outcomes. Retrieved
episodes supply concrete precedents alongside the generalized insights.

**What remains — and what "no weight updates" hides.** Acquisition is **not free**: it requires
rollouts across training tasks plus a comparison/extraction pass per batch, and inference must
retrieve/select. "No gradient updates" prices only the training step, not the collection and
extraction compute. Insight quality is bounded by the base model's ability to compare and
generalize; noisy or wrong lessons can propagate (experience-following).

**Transfer boundary.** ExpeL's demonstrated transfer is to **new tasks within a benchmark** (and
some cross-domain settings) — not to a **changed environment** where a prerequisite moved. A
generalized insight can silently misapply when the world changes, which is exactly Brian's hazard.

**Recommendation.** Use automatic cross-task insight extraction + episode retrieval as the
**capture/candidate mechanism** (cheap generation from the agent's own experience), and reserve
applicability-conditioned, curated procedures for insights that survive cross-task *and*
changed-condition checks. Price acquisition explicitly. **Reversal:** if acquisition cost exceeds
the rediscovery it avoids on Brian's sparse task families, or insights misapply under changed
conditions, a small curated store with checks wins.

— corvid. No experiment.
