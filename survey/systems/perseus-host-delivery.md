# System card: Perseus host delivery (installed hooks + published files)

**kiln · 2026-09-26 · source: perseus-ctx 1.0.26 wheel, `perseus.py` targeted ranges (hook templates ~26302, Claude install ~26463, watch ~31158, render ~30521); read-only extraction, no import/run. Lead cards (context-engine, ledger) + receipt c78 as context. Quoting ROLES fit duty. Roadmap inputs, principles, matrix requirements 2/4/8 as context.**

## Shipped integration vs rendered filename (separated)

- **Installed by command:** the Claude target runs an installer merging `SessionStart` + `UserPromptSubmit` hooks (`perseus render <source>`) into `.claude/settings.json` — a real install routine with dry-run, not a filename suggestion. Cursor gets an appended auto-generated block; other formats are file outputs.
- **AGENTS.md publication:** rendered file output (atomic writes) consumed through Pi's native loader — publication without refresh: Pi reads it at session start; nothing re-renders it per prompt.

## Refresh, dependencies, owner, test (proposed, not run)

- **Active-consumer refresh:** on Claude, every prompt submit re-renders the source — active sessions stay current without new glue. On Pi, refresh is session-start (or explicit reload); the watch path covers only the top-level source mtime, not included files or external state.
- **Owner:** Perseus upstream for the compiler; the operator who runs install for deployment. No new glue on the Claude path; Pi refresh still wants either watch-scope widening or the reload call.
- **Proposed test:** hook presence in settings + render freshness after source edit on Claude; AGENTS.md mtime + Pi session pickup on Pi. Unexecuted.

## Opinion: coherent delivery pilot on Claude, file drop on Pi

This removes more work than native files alone *where its hooks run*: compile-once, per-prompt refresh, multi-format output — a coherent supplied mechanism in one place. On Pi it is a better file drop, not delivery. It changes nothing on budgets, protected rules, or obedience. Recommend as the delivery-side pilot candidate for Claude alongside (not instead of) the guard pilot; Pi keeps native files + reload. **Medium confidence** (call paths read; nothing executed).
