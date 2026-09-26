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

## Tern qualification — budget target, not guaranteed cap

Lead source inspection of the same cached v13.27.1 confirms the reduction ladder, but `Pe` returns the remaining text with `overBudget:true` when no reduction remains. Caller `an` logs at debug level and returns text/stats. Therefore replace the unconditional removal claim with **automatic reduction of oversized injection, with a residual-overage path**. The target counts JavaScript string length, not tokens or bytes. Worker outage visibility is separate from whether this particular overage reaches the user. Hook declarations, including compact refresh, are implementation evidence; active registration and actual loaded output on Brian’s target host remain untested. This qualification changes no pilot recommendation. [Lead synthesis](../panel-response-c71.md).


## Tern cycle78 recheck — automatic prompt relevance is implemented

Re-inspected cached **13.27.1** `hooks/hooks.json` and `scripts/worker-service.cjs` statically; [bundle hash](../receipts/c78-perseus-source-20260926.json). UserPromptSubmit calls `session-init`. With `CLAUDE_MEM_SEMANTIC_INJECT=true`, a non-media prompt of at least20 characters goes to `/api/context/semantic`; default setting is **false**, default result limit5 (endpoint clamps1–20). The route searches project-scoped observations and injects titles, dates and **narratives**, not just index entries, as `hookSpecificOutput.additionalContext`. The acting agent need not decide to search on this enabled path. Empty results, search exceptions or worker fallback yield no additional context; project exclusions/private prompts also skip. Active registration and Brian's setting were not inspected or changed.

Correct requirement5's old “procedure selection remains actor owned” qualifier: the supplied optional selector is automatic. Keep **partial** because retrieved observations are not a procedure-specific applicability contract, exclusions/failure paths remain, and correct relevant delivery has no independent outcome evidence here. This rating is not withheld merely because obeying injected guidance is unproven: delivery and obedience stay separate. Requirement4's wording likewise now includes optional prompt-matched narratives. The SessionStart recency index and prompt semantic path must not be collapsed into a single selection mechanism; the10k-character reduction ladder was traced for the former, not established for the latter.
