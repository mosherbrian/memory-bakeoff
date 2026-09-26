# System card: Cradle (integrated perception/skill-curation/memory)

**kiln · 2026-09-26 · sources: paper v3 full methods (arXiv:2403.03186v3 PDF, §§1–5: six modules, procedural/episodic memory, ablations; ICML2025 edition NOT merged) + author repo BAAI-Agents/Cradle (environment/skill_registry.py, memory/local_memory.py, per-app atomic_skills; read-only clone, nothing executed). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## One skill's life (supplied → learned → stored → selected → executed → revised)

- **Origin:** pre-defined atomic skills per app/environment *or* generated from scratch (in-game guidance, manuals, self-exploration).
- **Storage:** procedural memory holds code-form skills with doc comments; registry validates (code valid, doc format, name uniqueness) and persists; relevance via embeddings (ada-002 generation). Episodic side: recent history KV + periodic summarization + task guidance, with load/save.
- **Selection/execution:** task inference picks/updates skills; action planning instantiates with parameters; executor runs keyboard/mouse code. Registry supports overwrite, delete, protection-conflict checks — update/delete *mechanisms exist* (unlike several c37–42 loops).
- **Feedback/revision:** self-reflection evaluates last action + failure analysis from screenshots; skills updated/composed accordingly. Ablations: task inference + procedural memory carry the complex-task gains; vision-loss (Voyager-like) collapses.

## Scaffold that makes it work (not portable as a unit)

Screenshots-in/keyboard-out GCC loop, GPT-4o backbone, per-app environments with atomic skills, embedding relevance, trial budgets. Install cost for Brian: entire robot-game stack — absurd and beside the point.

## Portable vs integrated (c56 carried)

Portable, severally: code-form skills with doc requirements; registry overwrite/delete/protection checks as update semantics; episodic summarization; relevance retrieval; self-reflection on last action. Integrated-only: the six-module closed loop around screenshots. No second-reuse rule imposed; logs-vs-skills decided per case; successful exit coexists with changed conditions (no auto-invalidation claimed).

## Advice: **borrow registry semantics, watch the loop**

Overwrite/delete/protection-check + doc-validated registration is the most concrete skill-lifecycle machinery in the survey — adopt as convention (name-uniqueness, doc-format, explicit overwrite) at ~zero cost. The integrated loop stays watch: prototype game/software harness, benchmark-only evidence. **Medium-low confidence** (v3 methods + repo read; ablations cited, not re-verified).
