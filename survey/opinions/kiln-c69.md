# kiln (Practitioner) — c69: enforce the checkable, count the loadable

**kiln · 2026-09-26 · see systems/independent-memory-controls.md. Quoting ROLES.md: "install cost, failure modes, maintenance, fit".**

Three independent controls, none requiring actor diligence: PreToolUse interception blocks checkable violations before execution (docs-verified semantics; Brian's installed set unaudited); the MEMORY.md budget check converts silent truncation into a counted condition (measured: byte cap binds ~line 193, ~108 lines unloadable); scheduled mining starts extraction without the actor (pi-reflect/ReMe/Hindsight paths specified, none recommended). Residual: uncovered tools, unknown Pi veto, fallible extraction, unmeasured obedience. Another file discipline would be status quo — these change what happens when memory is ignored. **Medium confidence** (mechanisms verified in docs/source/measure; installed behavior and obedience unmeasured).

## Design-constraint qualification (same cycle, sponsor constraint)

No build recommendation follows: measured against one-characterizable-design (named components, each contract, operational owner, tests), every candidate below is a research option, and my c69 "post-commit nudge script" is withdrawn (new script, disfavored).

| Candidate | Components (named?) | Contract status | Operational owner | Tests | Custom glue burden |
|---|---|---|---|---|---|
| ReMe (adopt) | workspace + MCP server + Stop-hook + dream cron (yes) | capture best-effort *silent-fail* — failure invisible by design; recall tools documented | upstream Agentscope; deployer unnamed (defaults to Brian — not assigned) | none run here; dream quality unvalidated | MCP/host wiring ×3, keys, backup, failure visibility |
| Hindsight (adopt) | daemon/server + hooks + MCP + per-repo bank (yes) | auto-recall/retain documented, fail-open cloud; consolidation gaps silent | upstream Vectorize; deployer unnamed | none run here; lifecycle unevaluated | daemon/PG ops or billing, bank scoping, silent-gap monitoring |
| Pi reflection (adopt) | extension + scheduler + guarded edits + metrics (yes, best-characterized) | edit guards source-verified; schedule/notify operator-side | tiny upstream (bus factor) + schedule operator unnamed | 137 claimed, none run | scheduler, log review; Pi-only, no Claude path |
| claude-mem | **gap: not source-audited by me** | — | — | — | — |
| Compose: one hooks-config | settings.json (deny + inject + budget-check) | hook semantics docs-verified; cross-host settings sync custom | editor-of-settings unnamed | none run | per-host sync (3 hosts), script upkeep |

| Compose: one hooks-config | settings.json (deny + inject + budget-check) | hook semantics docs-verified; cross-host settings sync custom | editor-of-settings unnamed | none run | per-host sync (3 hosts), script upkeep |
| hooks-config scripts | every invoked script/dependency named in the design (block-script, budget-check command, inject command) — no hidden glue | enumerating ≠ verifying | same unnamed editor | none run | — |

Closest to characterizable is the hooks-config (fewest parts, verified contracts) — but owner unnamed and cross-host sync unowned, so it withholds too. Missing everywhere: a named operator who is not Brian, and acceptance tests run against Brian's hosts. Until then: research options, no build.

## Pilot proposal (recommended before any execution; tests not run)

- **Named pilot:** one Claude host, one PreToolUse deny hook (single checkable preference, sponsor-scoped, e.g. python-not-python3 on covered Bash/tool paths) + one index-budget check command run read-only. No other hosts, no mining, no service.
- **Proposed owner (proposal, not assignment):** survey operator seat for pilot duration; long-term owner unresolved — explicitly unknown, not Brian by default.
- **Acceptance tests (design requirements, unexecuted):** ignored reminder still blocked on the covered path; oversized index flagged by the budget check; quoted correction not counted as recurrence; hook failures logged visibly. Unknowns listed: installed hook set, actual loaded prefix, obedience rate, Pi/local parity — none blocking the recommendation, all recorded for the pilot to check.
