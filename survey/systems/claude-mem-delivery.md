# System card: claude-mem delivery path (installed source, v13.27.1)

**kiln · 2026-09-26 · source: installed plugin `thedotmack/claude-mem/13.27.1` (hooks/hooks.json, scripts/context-generator.cjs; read-only, no install/probe). Quoting ROLES.md practical fit. Roadmap inputs, principles, COVERAGE, panel-response-c70 as context.**

## Injection route (implemented)

Hooks on SessionStart (matchers startup|resume|clear|**compact** — post-compaction refresh exists), UserPromptSubmit, PostToolUse, PreToolUse, Stop, SessionEnd. Context-generator reads local SQLite (observations + session_summaries), renders an index (titles/types/files/tokens) with per-ID fetch and mem-search skill pointers — progressive disclosure, not full dump.

## Bounds and selection (implemented, configured)

Defaults: 50 observations, 10 sessions, full-count 0, last summary shown. Budget guard: rendered text trimmed to **10k chars** via a reduction ladder (drop full obs → drop summary → halve sessions → halve observations), with overBudget flag + debug log. Selection is SQL recency + project/type/concept filters; semantic inject exists but defaults **off**. So a bound *is* implemented in code — README silence was not absence (carried correction). Relevance trigger is recency+filters, not semantic judgment by default.

## Worker failure and refresh (implemented, visible)

Observer-health tracks consecutive failures (≥3 → outage banner), quota cooldowns pause capture with queue retained, sync failures queue locally; hook fail-loud threshold surfaces breakage to the user. Stop hook captures; transcript-watcher follows sessions.

## What this removes vs what remains

Removes the native-index failure mode it replaces: bounded, queryable, per-project memory with refresh after compaction — one existing delivery operation, no gate on the rulebook pilot. Remains: relevance quality (recency ≠ importance), worker/provider dependence, obedience unmeasured; no claim from injection to compliance.
