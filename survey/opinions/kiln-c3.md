# kiln (Practitioner) — c3: one portable record across three hosts

**kiln · 2026-09-26 · ≤500w · recommendation only, no installs. Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Sources: current Claude Code memory docs (read c2), pi-lcm primary notes (c2-continuation), roadmap inputs, BRIAN-PRINCIPLES.**

## The problem

Three hosts, three loading mechanisms, one Brian. Copies multiply: a preference fixed in repo CLAUDE.md but stale in auto memory; a procedure improved on Pi but fossilized in a local agent's prompt. Every extra copy is a future contradiction, and contradictions resolve arbitrarily.

## Canonical source vs views

- **Canonical source: one versioned markdown repo** (preferences with scope/source/date, textual skills, runbooks with outcomes). Edited by hand, reviewed by commit. This is the only thing anyone edits directly.
- **Views are generated or imported, never authored:** Claude Code reads them via `@import` lines in CLAUDE.md (docs-supported, recursive to depth 4) or path-scoped rules pointing at the checkout; Pi-side content enters through whatever the Pi harness loads from disk (exact mechanism **unknown from my reading** — deepen next); local agents get the relevant slice inserted into their prompt/harness context by the operator at run time.
- **One-way flow, single-writer rule:** canonical → views. A correction discovered on any host gets written to canonical first, then flows out. Host-local overrides live only in named local files (`CLAUDE.local.md`, Pi-local config) and lose to canonical on conflict by documented convention — with the c2 caveat that nothing enforces this except discipline.

## What each host actually loads (knowns and unknowns)

- **Claude Code:** known — tiered CLAUDE.md scopes + MEMORY.md index (200 lines/25KB cap) every session, topic files and skills on demand. View mechanism (imports, rules) is docs-supported. Install cost ~zero.
- **Pi:** now partially known (read-only look this session): the Pi agent boots from a dedicated agent dir (`PI_CODING_AGENT_DIR`, e.g. `acp-pi/.pi-agent/`), with `settings.json` config plus workspace instruction files in the same pattern as Claude Code's project memory — and pi-lcm's SQLite store sits alongside as a tool-callable FTS archive, not an auto-loaded context layer. So the Pi view path is real: canonical files checked out or symlinked into the agent dir (cf. existing auth/models symlink practice), with pi-lcm as on-demand recall. **Medium confidence** (workspace docs + primary-notes; Pi binary's exact load order not verified).
- **Local agents:** unknown per harness — assume nothing loads unless the operator puts it in context. Cheapest assumption, fewest surprises.

## Minimum arrangement I would use

One canonical repo; Claude Code views via imports; Pi/local views as operator-inserted slices; auto-memory left on as capture net feeding corrections back to canonical; no new service. Update burden: one edit location, three view paths to spot-check. Failure mode is view drift — mitigated by keeping views mechanical (imports, not copies).

**Medium confidence** in the shape; Pi view path now read-only-confirmed at the workspace level, binary load order still unverified.
