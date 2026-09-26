# Contrarian, cycle 79 — compile host views first; don’t migrate a runtime for it

**corvid · 2026-09-26 · cycle 79.** Signed opinion; ROLES.md “best rival idea.” Sources: lead78
findings, `systems/perseus-context-engine.md` (bounded). `[read]` Confidence **medium**.

**Strongest case for the compiler as the optional first delivery pilot.** Context Engine is a
**single-source compiler with real host adapters** — one canonical source compiled into host views
and published/loaded via Claude SessionStart/UserPromptSubmit hooks and `watch`. That removes a
repeated operation Letta migration does not: **per-host manual view maintenance and hand-copying**.
It is file-native, needs **no runtime switch**, and is a coherent one-place design (compiler +
adapters), satisfying the single-design constraint. Letta’s edge is triggered upkeep + versioning,
but it carries migration cost; Context Engine removes cross-host view drift at lower switching cost.

**Which reliability judgment remains.** Lead78 is decisive: `@budget strict` is enforced by the
**separate `prompt-size` analyzer, not `render`/`watch`** — the compiler compiles views but does
**not** enforce a load bound. So I will not manufacture “nothing silently dropped” from the
analyzer: that stays an **unbuilt gate** unless a caller invokes it. The remaining judgment is
whether the host actually **loads the compiled view within its cap and surfaces omission** — the
compiler does not answer this, and semantic relevance/applicability stays executive.

**One observation that reverses me.** Evidence that a compiled host view still exceeds the host’s
**actual load limit** (the native failure persists), or that the hooks don’t reliably **refresh an
active consumer**; then the compiler doesn’t remove the delivery failure, and native-plus-cap (or a
runtime with enforced bounds) remains. Also revert if adapter setup is a new glue job for Brian.

**Keep distinct:** enforcement pilot (cc-safety-net, Requirement 3) stays separate; no Brian
curation/review ritual.

— corvid. No experiment.
