# kiln (Practitioner) — c51: one correction, three hosts, traced

**kiln · 2026-09-26 · ≤350w · design example ("use pnpm here"), not a real instruction. Existing cards only. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

| | Durable source | Load trigger | Corrects active context? | Evidence vs unknown |
|---|---|---|---|---|
| Claude Code | repo CLAUDE.md line or user-scope note (implemented) | session start / `/context` reload (implemented); imports live | No — loaded context stays until next session/reload; a mid-session correction waits (docs-verified behavior) | implemented |
| Pi | canonical file in/visible to agent dir (convention) + pi-lcm session record (implemented) | session start; pi-lcm recall is per-query tool call (source-read) | Partly — a fresh recall surfaces it, but already-injected context is not rewritten (inferred from adapter shape) | mixed: paths source-read, refresh timing unknown |
| Local agent | operator-inserted slice or harness file (convention) | run start (convention) | No — frozen at launch (by construction) | convention throughout |

Bytes stored (one line, versioned) ≠ hosts loaded (three different triggers, none push) ≠ model applies (selection + judgment per turn) ≠ useful outcome (next pnpm-run actually uses pnpm). No host loads every correction, and none should — scope ("here") is a project path, and the table shows each host resolving it its own way.

## Smallest automation worth building, if needed

A post-commit hook that diffs preference files and nudges affected hosts (re-open hint on Claude, re-pull on Pi checkout, re-slice note for local runs) — removes the human sync ping, nothing more. Not a deployment: a script behind the tripwire, built when hand-carrying recurs, not before. Retrieval remains unsolved on all three rows; no universal receipt or self-test is imposed — the correction carries a validity line and the next run is the audit.

**Medium-low confidence** (paths from inspected sources; timings partly inferred, marked).
