# kiln (Practitioner) — c52: Pi loads once, from the obvious places

**kiln · 2026-09-26 · see systems/pi-instruction-delivery.md. Quoting ROLES.md: "install cost, failure modes, maintenance, fit".**

Pi's loader is documented in its own source: first-match-per-directory (AGENTS.override > AGENTS > CLAUDE), global agentDir plus ancestor walk, skills as name+description at startup with body-on-match. The cheap canonical route is real — one file, next session. What's missing is in-session refresh (unverified, not assumed) and cross-session recall past pi-lcm's per-conversation scope. No new harness claimed, no hooks imposed. **Medium confidence** on discovery/selection (source-read); low on reload (searched, not found).
