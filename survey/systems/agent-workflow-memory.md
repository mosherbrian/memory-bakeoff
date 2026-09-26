# System card: Agent Workflow Memory (offline/online routines, guidance vs tool)

**kiln · 2026-09-26 · sources: paper full methods arXiv:2409.07429v1 (§§1–5) + author repo zorazrw/agent-workflow-memory (webarena/mind2web harnesses, offline_/online_induction, prompt templates; read-only clone, nothing executed). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Stored form, parameterization, selection/insertion

- **Form:** workflow = NL description d + step sequence (state-NL + reasoning + executable action program), with example values abstracted to placeholders ({product-name}). Sub-routine granularity, not whole trajectories.
- **Protocols (kept separate):** offline = batch induction from canonical examples → one memory for all tests; online = streaming induce/integrate/utilize per test, gated by an LM evaluator's binary success label. Mind2Web evidence is offline step-accuracy; WebArena is online execution success — different claims, not pooled.
- **Selection/insertion:** per-website grouping keeps the collection small; insertion appends into memory/prompt (M+W). No contradiction management, no deletion/retirement path described — the store grows (snowball celebrated, pruning unaddressed).
- **Guidance vs executable tool (separate variants):** AWM memory augmentation vs AWMAS callable workflow-actions. AWMAS: +1.3 step SR, same task SR, agents invoke the tool in only 18.5% of tasks, and pre-determined sequences break on dynamic states (flight pop-up counterexample). Guidance transfers; executables rigidify.

## Induction trigger, validation, removal, host burden

Trigger: offline batch or online post-success (evaluator-gated). Validation: LM evaluator binary + execution success; removal: none reported. Host burden: benchmark envs, GPT-4-class models, evaluator calls, per-website grouping discipline. Repo is benchmark harnesses + prompts — prototype, no host adapter, no maintained plugin.

## Advice: **borrow sub-routine abstraction, watch the loop**

The portable piece is parameterized sub-routines with abstracted slots — a better skill format than whole transcripts, and the AWMAS result argues for keeping them as *guidance* rather than tools. The induction loop (evaluator-gated, snowballing, no retirement) stays watch: no deletion story, benchmark-only evidence. **Medium-low confidence** (methods + repo read; numbers cited, never compared across settings).
