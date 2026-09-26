# Source card: native failed-attempt recovery on Pi/pi-lcm

**kiln · 2026-09-26 · source: pi-lcm v0.1.3 `src/db/store.ts` + `src/tools/lcm-{grep,expand}.ts` (read-only, this session); Claude Code docs as cited. No transcript content exposed. Quoting ROLES.md: "maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## The actual route (no message ID needed)

1. **Search → IDs:** `lcm_grep` (agent-callable tool) searches message text via FTS5 (with LIKE fallback) or regex, over `messages` / `summaries` / both scopes, with snippet output, time filters, and result caps. Every hit returns message/summary IDs; message hits are enriched with covering-summary info (`summary_id`, depth) via `summary_sources`.
2. **ID → expansion:** `lcm_expand(summary_id, depth ≤ 3, token budget ≤ 8000)` drills a summary back to original messages through `summary_sources` (cycle-guarded); `getMessagesByIds` fetches messages verbatim; `getMessages(conversation, from/to/role)` reads a seq window around a hit — the failed attempt's *sequence*, not just the error line.
3. **Stored vs transformed:** originals are stored verbatim (`content_text` + `content_json`, dedup-hashed); summaries are derived alongside and linked, never replacing. Recovery reads the original, not a reconstruction — strictly stronger than episode-reconstruction on this axis. A prior failed procedure is findable by its error text, tool name, or time window without any ID.

## What still needs custom glue (concrete)

- **Cross-conversation sweep:** every search/store call is scoped to one `conversation_id`. Finding last month's failed rollout means iterating conversations — no global search exists. Glue: a small loop over conversation IDs (read-only SQL the schema already supports).
- **Outcome marking:** nothing records pass/fail. "Failed" is a judgment the agent makes from content (error text, retry loops, user correction) at recovery time. Glue: a convention for marking (e.g. a failure note appended to the canonical skill/runbook with the seq window), not new infrastructure.
- **Staleness of the recovered attempt:** recovery returns what happened, never whether it still applies — the c6 narrow/repair judgment stays with the agent.

## Verdict on the mechanism: **deploy (it already is)**

The whole route ships in the installed stack at zero marginal cost: grep → IDs → expand/seq-window. What is missing is two inches of glue (cross-conversation loop + failure-note convention), both expressible with existing calls. Claude Code side is thinner — file grep over discrepant stores plus `/memory` audit, no structured expansion — so Pi/pi-lcm is the reference implementation of native recovery, and the c13 "unbuilt glue" shrinks to the sweep loop.
