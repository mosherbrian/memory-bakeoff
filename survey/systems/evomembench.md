# System card: EvoMemBench (evaluation harness, not facility)

**kiln · 2026-09-26 · sources: paper 2605.18421v2 (abstract + methods excerpts via HTML/search) + official repo DSAIL-Memory/EvoMemBench (top-level layout; read-only clone, nothing executed). Identity verified, distinct from EvoArena 2606.13681. Quoting ROLES.md practical fit. Roadmap inputs, principles, RECOMMENDED-DESIGN, COVERAGE as context.**

## Execution path (what a host supplies)

Four task dirs (InEp-Know 2800 MemoryAgentBench; InEp-Exec 800 BFCL-MultiTurn-LongContext; CrossEp-Know 884 CL-Bench; CrossEp-Exec) with launch scripts + data loaders; per-system eval adapters (mem0, A-mem, MemOS, memagent + task-level retrieval/workflow/reasoning-bank baselines). A host supplies: model APIs + embeddings (+ vLLM deployment for memagent), datasets, compute, standardized protocol runner. Feedback/labels come from the task datasets themselves; reset rules are per-task harness conventions. No reusable method, store, or adapter ships — only task code, data pointers, and system-specific eval glue.

## Portable artifact vs benchmark

None portable. The durable outputs are the four-quadrant taxonomy and the finding set: long-context baselines highly competitive; memory helps most when current context is insufficient or tasks are difficult; no single memory form wins; retrieval dominates knowledge settings, procedural/long-term wins execution *when stored experience matches task structure*. Those conditionals refine *when* our arrangement's pieces pay off — they add no component.

## Capability-matrix change: none

Per commission: pure benchmark stays in the footer; no product row fabricated. No cell changes — the findings corroborate existing placements (retrieval for knowledge, procedures for matched execution, long-context as the rival to beat) without moving any.

## Verdict: **read, use the conditionals, build nothing**

Signed: harness inspected at layout level, methods via paper excerpts (not full-methods read — marked). Cost/ownership boundary: running it would cost models + compute + protocol labor for a ranking Brian doesn't need; the decision-useful content is already extracted above. **Medium-low confidence** (identity + structure verified; findings via excerpts, no independent methods audit).
