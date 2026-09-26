# Reading note c72 — EvoMemBench: what is retained, who supplies feedback, what the controls isolate

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 72.**
Skeleton first; **one primary: arXiv 2605.18421v2, identity verified before methods** (queued as
EvoMemBench, Yuyao Wang et al., distinct from EvoArena/EvoMem 2606.13681). If identity fails,
bounded failure report, no substitute sweep. Charge: retention across in/cross-episode tasks;
knowledge vs execution; same-executor memory-on/off or representation control; feedback/label
provenance; held-out units; changed-environment reuse; cost accounting; strongest action-changing
limitation; author evaluation vs independent benefit. One discriminating result maximum. No
sweep/probe/install.

*(facts + verdict appended below)*

## Identity (verified before methods)

**arXiv 2605.18421v2 — "EvoMemBench: Benchmarking Agent Memory from a Self-Evolving
Perspective," Yuyao Wang et al., 18 May 2026** — confirmed distinct from EvoArena/EvoMem
2606.13681. A **pure evaluation harness**: six reconstructed datasets (four source benchmarks,
incl. MemoryAgentBench subsets, BFCL-Multiturn-LongContext) on two axes: **scope** (in-episode vs
cross-episode) × **content** (knowledge vs execution).

## Controls and provenance

**Same-executor control: yes, and it's the design.** All 15 memory methods run on a **unified
DeepSeek-V3.2 backbone**; source pipelines reused, only backbone replaced or memory attached;
memory-free Gemini-3-Flash / GPT-5-mini / DeepSeek baselines. **Held-out units:** episodes
separate; **cross-environment transfer** tested — memory built on a source subset, **kept fixed**
for a target subset. **Feedback:** environment-provided verifiable outcomes (tool results, goal
success); accuracy/success plus **token usage including the memory module's own inference cost**
— cost accounting present. **Revision vs retention** is separated inside InEp-Know
(FactConsolidation multi-hop).

## The one discriminating result

**Finding 2: methods are better at retention than revision — BM25/Mem0/A-MEM beat no-memory on
retention but drop sharply on multi-hop FactConsolidation; the authors name the bottleneck as
"deciding which stored information should be updated, suppressed, or replaced when later evidence
conflicts."** That is the c68 STALE adjudication gap reproduced on a different benchmark, with a
fixed executor — the corpus now has **two independent author groups** locating failure at
authority, not storage.

Supporting, non-headline: strong long-context baselines stay highly competitive when budget
suffices (Finding 1); memory's marginal benefit **shrinks as context budget grows** 16K→128K
(Finding 3) and memory **hurts easy tasks** (Finding 5); procedural guidance is the strongest
execution form (Finding 4); transfer is stable only where decision procedures match (Finding 8).

**Limitation that changes action:** everything is **author-assembled from existing datasets**
with author-chosen splits and difficulty labels; gains are harness-relative — **no independent
realistic-benefit measurement exists**, and no method is offered for adoption. Read findings as
protocol-relative orderings, not field rates.

**Verdict: a competent matched-executor harness whose value to this panel is confirmatory — it
independently reproduces the storage-vs-authority split and prices memory in tokens — and adds no
adoptable mechanism.** Recommendation impact: none; capability-matrix entries for memory products
may cite Finding 2 as second-source evidence, nothing more.

**Confidence: high on design facts (explicit protocol), high on Finding 2's isolation (same
backbone, subset-level deltas), medium that easy/hard splits transfer as difficulty notions
(author-labeled).**

— cairn. Inputs: ROLES.md, BRIAN-PRINCIPLES.md, both roadmap inputs, COVERAGE.md,
RECOMMENDED-DESIGN.md, CAPABILITY-MATRIX.md context.