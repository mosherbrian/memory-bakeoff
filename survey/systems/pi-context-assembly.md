# System card: Pi context assembly (loader → system prompt → request)

**kiln · 2026-09-26 · source: earendil-works/pi @ 2b0a123 (current main HEAD at read time — same hash as the old badlogic snapshot, so equivalence holds for this read; `core/resource-loader.ts`, `core/system-prompt.ts`, `core/agent-session.ts`; read-only clone, no runtime/probe). Quoting ROLES fit duty. Roadmap inputs, principles, matrix requirements 2/4 as context.**

## Assembly path (source-verified)

`loadProjectContextFiles` (agentDir global + ancestor walk, first-match per dir) → `agent-session` feeds loaded files + skills into `normalizeBuildSystemPromptOptions` at session setup → `renderProjectContext` wraps each file whole in `<project_instructions path=...>` blocks → system prompt per request. Skills: names/descriptions at startup, bodies on match.

## Bounds, omissions, exclusions, refusal

- **Oversized files:** no size cap, truncation, or budget found anywhere on this path — full content rendered. No enforced bound exists to verify.
- **Unreadable files:** yellow console warning + skip (visible on terminal, not to the model, not logged structurally).
- **Exclusions:** `noContextFiles` flag, per-resource overrides, worktree-shadow dedup. No refusal-of-whole-load mechanism found.
- **Refresh:** reload() accepted from the c52 correction (upstream facility); auto-refresh on edit not evidenced — delivery is session-setup (+ explicit reload), not continuous.

## Cell deltas proposed (requirements 2/4)

- **Req 2 (bounds): no change — stays unknown.** Automatic delivery scope is now verified, but no enforced load bound exists in the inspected path; absence of a bound is not a bound. Do not manufacture partial from delivery alone.
- **Req 4 (delivery): no change — stays partial,** qualifier narrowed: scoped startup loading verified into every system-prompt build + upstream reload facility; active-session refresh requires explicit invocation, skill bodies need selection. Installed behavior still unknown.
