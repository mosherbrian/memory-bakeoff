# System card: OS-Copilot/FRIDAY (self-directed tool acquisition)

**kiln · 2026-09-26 · sources: paper full methods 2402.07456v2 (§§1–4, App. A–D) + author repo OS-Copilot/OS-Copilot (friday_agent.py run/self_refining/planning/executing/judging/replanning/repairing; tool_repository/{api,basic,generated,manager}; read-only clone, nothing executed). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## One tool's life (acquisition → storing → retrieval → execution → correction)

- **Acquisition:** 4 seeded basic tools; self-directed curriculum proposes easy→hard tasks per unfamiliar app; tool generator writes Python/API tools; critic scores reuse potential 0–10, keeps >8; max 3 repair attempts per subtask. SheetCopilot: 0% → 60% after 10 self-set tasks, 8 tools kept.
- **Storing:** tool repository (api/basic/generated + manager); declarative side holds user profile (conceptual per paper) + semantic knowledge (trajectories, OS state).
- **Retrieval/execution:** dense retrieval into working memory; executor runs via universal runtime (Python/bash/API/mouse-keyboard); DAG planner parallelizes independent subtasks.
- **Correction:** critic judges completion from before/after system state (no ground truth — LLM-judged); refiner repairs action/tool/subtask; DAG replanning on failure.

## Interfaces, evaluator, goals (who supplies what)

Interfaces: OS-supplied (apps, APIs, files) + 4 seeds + generated code. Evaluator: LLM critic on system-state diffs (fallible by construction; App. D admits ground-truth-free assessment limits) + benchmark servers (GAIA submission, SheetCopilot-20). Goals: self-proposed curriculum + user requests + DAG decomposition.

## Excel/PowerPoint vs GAIA endpoints (separated)

SheetCopilot/PPT: single-app mastery via self-curriculum (0→60%, qualitative PPT slides). GAIA: cross-app generalization, 40.86 L1 (+35% rel), dev-set tool accumulation (4→13 tools) then frozen test. Different claims: app mastery vs generalization — not pooled.

## Host burden / advice: **watch the curriculum pattern, not the OS harness**

Interfaces supplied by the OS, evaluator LLM-judged, goals half self-proposed: the portable piece is self-directed curriculum (easy→hard self-set tasks + score-gated retention) for any unfamiliar tool/API — the closest to a "learn this software" procedure on the roster. The harness (Linux/macOS runtime, DAG planner, GPT-4) stays watch: prototype research code, benchmark-only evidence, critic fallibility unpriced. **Medium-low confidence** (paper + repo read; costs unledgered).
