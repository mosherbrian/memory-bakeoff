# System card: Pi instruction delivery (pi-mono source)

**kiln · 2026-09-26 · source: badlogic/pi-mono, packages/coding-agent (v0.87.1, commit 2b0a123; `core/resource-loader.ts`, `docs/skills.md`; read-only clone, no install/probe/secrets). Quoting ROLES.md: "install cost, failure modes, maintenance, fit for Brian's stack". Roadmap inputs + principles as context.**

## Project instruction discovery (source-verified)

- Per directory, first match wins: `AGENTS.override.md` > `AGENTS.md` > `AGENTS.MD` > `CLAUDE.md` > `CLAUDE.MD`. One file per directory — a CLAUDE.md beside an AGENTS.md is silently skipped.
- Scopes loaded: agentDir global (e.g. `~/.pi/agent`) first, then ancestor walk from cwd to filesystem root (nearest last, so deeper files read later), with worktree-shadow dedup. Loaded once in the resource loader (`this.loaded = true`).
- **Reload: no active-session reload path found** in inspected code — marked unknown, not absent. A mid-session correction to AGENTS.md has no verified re-read; fresh session is the confirmed route.

## Skill loading (docs-verified)

Agent Skills spec: startup scan of configured locations (user/project `~/.agents/skills/`, `.agents/skills/`, ancestors to repo root); name+description+path into the system prompt, body only on task match; `/skill:name` forces; `disable-model-invocation: true` for manual-only. Docs admit the miss case ("A model might fail to load a relevant skill").

## Cheap route + missing operation

Cheap route exists today: a canonical project source is one AGENTS.md edit (or symlink into it) read at next session start — zero install, zero service. Missing operation, exactly: **in-session refresh** (no verified re-read of edited instruction/skill files) plus **cross-session recall** beyond pi-lcm's per-conversation store. No hook/validity-line/audit imposed — the gap is a reload call and a recall habit, both smaller than any service.

## Addendum: reload reconciliation (c52 correction)

- **My snapshot:** cloned `badlogic/pi-mono` (now redirecting to `earendil-works/pi`), read as v0.87.1 / commit 2b0a123. Exact snapshot link: `https://github.com/earendil-works/pi` at that commit — equivalence with moving `main` unestablished.
- **What I searched:** reload-named variants (`reloadResources`, loader re-`load`, compaction-triggered reload) — **not** a bare `reload()` method on the resource loader. So my "no reload path found" covers my search terms, not the file exhaustively.
- **Tern's finding (moving main):** `resource-loader.reload()` exists, calls `loadProjectContextFiles`, reassigns `agentsFiles`; `loaded` governs cache handling, not one-time loading; `agent-session.ts` exposes `reload()`; configuration docs direct `/reload` after instruction edits. Discovery order agrees with this card.
- **Reconciled position:** an upstream reload facility is source-evidenced on moving main; whether it exists in v0.87.1/2b0a123 or on Brian's installed host is unknown. "Missing refresh operation" is withdrawn as a current-product claim and replaced with: verify installed version + invocation from the relevant host mode + whether the correction governs the next action. Cross-conversation recall separated out — not needed for already-canonical directions.
