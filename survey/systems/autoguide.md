# System card: AutoGuide (context-keyed selection)

**kiln · 2026-09-26 · sources: paper full methods arXiv:2403.08978v2 (§§1–4, App. A–D). Author repo: not located in one bounded search (no GitHub link in paper excerpts or search results) — recorded as unlocated, worked from paper only. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Mechanics (source-visible)

- **Context representation:** NL description of the agent's status generated from the partial trajectory (M_context); near-duplicate contexts merged via LLM match at build time.
- **Store:** plain dict — context string → guideline set. Guidelines extracted from contrastive trajectory pairs (± reward) at the deviation timestep, conditional-structured ("when [context], do X").
- **Matching/retrieval:** at each timestep, identify current context; exact dict-key lookup; if matched, LLM top-k selection (k=3 best in ablation; k=5 overthinks); **no match → empty set, nothing forced** — honest abstention, a real design virtue.
- **No-match/conflict handling:** no-match handled (∅). Guideline-vs-guideline contradiction management: **unreported** in methods as read — no Consolidator, no voting, no deletion path described. The store only grows per build.
- **Host inputs:** offline contrastive trajectory pairs with rewards; same LLM throughout (action/context/selection); test-time per-step context ID + selection calls. **Update path:** re-run extraction offline in batch — no online loop (the precise gap vs AutoManual's Planner/Builder alternation).

## Vs AutoManual construction

AutoManual builds typed, example-grounded rules online with revision/deletion and formulates a manual; AutoGuide extracts conditional guidelines offline and *selects* per step. Complementary axes: AutoManual answers "what is the guidance," AutoGuide answers "which guidance now." AutoGuide's ablations isolate the contribution honestly (context-only 36, guidelines-only 37, full 46 on WebShop; selection beats whole-list ExpeL-style dumping, which confuses).

## Fit for Brian / advice: **borrow selection, watch the builder**

The conditional "when [context]" prefix + no-match-abstention + top-k cap ports directly into our skills today (it is formalized trigger prose with a silence default). The offline extraction loop stays watch: needs contrastive trajectory pairs Brian doesn't collect, and the store has no revision story. **Medium-low confidence** (methods read; repo unlocated; numbers not pooled across settings).
