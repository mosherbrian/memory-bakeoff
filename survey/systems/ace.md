# System card: ACE (playbook with counters + deterministic merge)

**kiln · 2026-09-26 · implementation + paper read (arXiv:2510.04618v1 §§1–4.6; author-linked repo github.com/ace-agent/ace: ace/core/{generator,reflector,curator,bulletpoint_analyzer}.py + playbook_utils.py, shallow clone, nothing executed). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context. Distinguished from third-party DannyMac180/ACE (MCP port, not inspected).**

## Mechanism (source-verified)

Playbook = itemized bullets in plain text: `[sec-00001] helpful=4 harmful=1 :: content`. Three roles: Generator solves with current playbook and marks bullets useful/misleading; Reflector distills delta candidates (up to 5 refinement rounds); Curator proposes operations; **code** merges deterministically (reducer dedups proposals, embedding-based similar-group merge, counters incremented in place). Grow-and-refine runs proactively or lazily. Numbers noted-not-imported: +17.1pp AppWorld online-unlabeled, −86.9% adaptation latency vs baselines, ablations crediting Reflector + multi-epoch. Honest limit stated in-paper: without reliable feedback (labels or execution signals) both ACE and Dynamic Cheatsheet degrade — adaptation depends on feedback quality.

## What complements native files (no code needed)

1. **Bullet format with counters** — portable as a markdown convention into our skills/preference files today: per-rule helpful/harmful tallies are finer upkeep granularity than pi-reflect's per-section recidivism, and they make "is this rule sticking?" answerable by reading.
2. **Delta-update discipline** — localized edits, never monolithic rewrite. This is the direct antidote to the context-collapse failure (18,282 → 122 tokens, accuracy below baseline) and should govern our canonical repo: append/increment/prune, never regenerate.
3. **Lazy refinement** — dedup only when the window demands it, matching our trim-on-checkup posture.

## What does NOT transfer without machinery

The three-role loop itself: it needs execution trajectories (Generator), a feedback signal that actually discriminates (Reflector — execution success/failure, tests, or labels), and rollout budget (batch-1, multi-round, multi-epoch). For Brian the "task evaluator" is outcome checks (build/test/verify runs) — real but narrow: it covers procedures with machine-checkable outcomes, not preferences or judgment calls. No evaluator, no curation — the playbook rots like any other file.

## Upkeep granularity vs pi-reflect

pi-reflect: whole-rule surgical edits + per-section recidivism + git history. ACE: per-bullet counters + embedding dedup + deterministic code merge + fine-grained per-query retrieval. ACE is finer-grained and retrieval-aware; pi-reflect is simpler (one LLM call, local files, no loop). They compose: ACE's bullet convention inside files pi-reflect maintains.

## Advice: **watch the loop, deploy the convention, medium-low confidence**

Adopt bullet counters + delta-only edits into our canonical files now (~zero cost); leave the Generator/Reflector/Curator loop on watch until a procedure with a real outcome check earns it. Paper + code agree on mechanics; all gains are benchmark-side, none on Brian-shaped tasks.
