# System card: CLIN (causal abstractions + meta-memory)

**kiln · 2026-09-26 · sources: paper full methods arXiv:2310.10134v1 (§§1–4, limitations) + author repo allenai/clin (format_memory, CLI flags; read-only clone, nothing executed). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## What persists; preserve vs replace

- **Persists:** NL causal abstractions in fixed syntax — "X is NECESSARY to Y" / "X DOES NOT CONTRIBUTE to Y" with may/should uncertainty markers — plus, in-repo, task + episode + evaluation report per learning (`PREVIOUS LEARNINGS` format).
- **Update semantics:** per trial, the generator *rewrites* the list from the latest trial + last-3 memories with saliency pruning (replace-with-pruning, not append). Across episodes, best-trial memories enter a fixed archive (10) compiled into generalized meta-memory. So: replace locally, archive-then-compile globally. Deleted abstractions leave no trace except the archive's winners.
- **Feedback/selection:** simulator rewards via 7 NL rules; controller selects memory items per state at act time; meta-memory built against the target task description. Retrieval misfires documented (gallium repeatedly retrieves stove-insight) — selection failure is admitted, not solved.
- **Host inputs:** ScienceWorld simulator (resets, admissible actions, rewards), gpt-4, trial budgets (≤5, stop at 100), archive size. Reset/retry: env resets per trial; memory persists across trials *and* episodes (the Reflexion contrast).

## Adaptation units (read before mapping)

Gen-Env = same task across varied objects/locations; Gen-Task = related tasks sharing objects (boil↔freeze). Both are new instances under shared rules, not changed rules — the stove-broken→lighter case varies configuration within one rule family. True prerequisite/rule changes are untested; mapping "adaptation" to Brian's changing software prerequisites overclaims. Transfer gains (+4 env / +13 task zero-shot, more with updates) hold inside that envelope.

## Prototype vs portable

Repo is a 2023 ScienceWorld harness (prototype). Portable at ~zero cost: the abstraction syntax with uncertainty markers, replace-with-pruning updates, best-of archive + meta-memory compile, and controller-side per-state selection. The simulator loop stays behind.

## Advice: **borrow the syntax, watch the loop**

Causal-abstraction format + uncertainty markers + archive-compile ports to native skills directly and answers "what survives a rewrite" better than our current notes. The loop needs resettable episodes with rewards — absent in Brian's lane. **Medium-low confidence** (methods + repo read; adaptation envelope carefully bounded).
